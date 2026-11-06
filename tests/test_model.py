import contextlib
import io
import os
import shutil
import tempfile
import unittest
import warnings

import numpy as np
import pandas as pd

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import moe_lstm

try:
    import tensorflow.keras.models as keras_models
except ImportError:  # pragma: no cover - exercised only when TensorFlow is absent
    keras_models = None


def _synthetic_frame(n_rows=40, n_features=3, seed=0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    frame = pd.DataFrame(rng.normal(size=(n_rows, n_features)), columns=["A", "B", "C"][:n_features])
    frame["Target"] = rng.integers(0, 2, size=n_rows)
    frame["Tomorrow_Change"] = rng.normal(scale=0.01, size=n_rows)
    frame["Date"] = pd.bdate_range("2020-01-02", periods=n_rows)
    return frame


@unittest.skipIf(keras_models is None, "tensorflow is not installed")
class ModelTests(unittest.TestCase):
    def test_mixture_output_is_a_probability_and_the_gate_sums_to_one(self):
        model = moe_lstm.build_moe_model(lookback=5, n_features=3)
        expert_names = [layer.name for layer in model.layers if layer.name.startswith("LSTM_Expert_")]
        self.assertEqual(expert_names, ["LSTM_Expert_1", "LSTM_Expert_2", "LSTM_Expert_3"])
        sample = np.zeros((2, 5, 3), dtype="float32")
        predicted = model.predict(sample, verbose=0)
        self.assertEqual(predicted.shape, (2, 1))
        self.assertTrue(np.isfinite(predicted).all())
        self.assertTrue(((predicted >= 0) & (predicted <= 1)).all())

        gate_model = keras_models.Model(
            inputs=model.input,
            outputs=model.get_layer("Gating_Network").output,
        )
        gate = gate_model.predict(sample, verbose=0)
        self.assertEqual(gate.shape, (2, 3))
        np.testing.assert_allclose(gate.sum(axis=1), np.ones(2), atol=1e-5)

    def _producer(self, tensor) -> str:
        history = tensor._keras_history
        operation = history.operation if hasattr(history, "operation") else history[0]
        return operation.name

    def test_sparse_top_k_gives_inactive_experts_zero_weight(self):
        import tensorflow as tf

        from moe_lstm.model import renormalized_top_k, switch_auxiliary_loss

        probs = tf.constant([[0.7, 0.2, 0.1], [0.2, 0.5, 0.3]], dtype=tf.float32)
        gated = renormalized_top_k(probs, k=1, n_experts=3).numpy()
        self.assertEqual(gated.shape, (2, 3))
        np.testing.assert_allclose(gated[0], [1.0, 0.0, 0.0], atol=1e-6)
        np.testing.assert_allclose(gated[1], [0.0, 1.0, 0.0], atol=1e-6)
        kept = renormalized_top_k(probs, k=2, n_experts=3).numpy()
        np.testing.assert_allclose(kept[0], np.array([0.7, 0.2, 0.0]) / 0.9, atol=1e-5)
        np.testing.assert_allclose(kept[1], np.array([0.0, 0.5, 0.3]) / 0.8, atol=1e-5)
        self.assertTrue(np.all((kept == 0).sum(axis=1) == 1))
        np.testing.assert_allclose(kept.sum(axis=1), np.ones(2), atol=1e-5)
        loss = float(switch_auxiliary_loss(probs, k=1, n_experts=3))
        # Both windows dispatch to a different expert, so f is not a point mass.
        # Row means: P = [0.45, 0.35, 0.2]. Dispatch f = [0.5, 0.5, 0].
        self.assertAlmostEqual(loss, 3 * (0.5 * 0.45 + 0.5 * 0.35), places=5)

        model = moe_lstm.build_moe_model(lookback=5, n_features=3, top_k=1, aux_loss_weight=0)
        self.assertEqual(model.output_shape, (None, 1))
        self.assertEqual(self._producer(model.get_layer("Weighted_Sum").input[1]), "Sparse_Gate")
        self.assertEqual(self._producer(model.get_layer("Sparse_Gate").input), "Gating_Network")
        sample = np.random.default_rng(0).normal(size=(4, 5, 3)).astype("float32")
        predicted = model.predict(sample, verbose=0)
        self.assertEqual(predicted.shape, (4, 1))
        router = keras_models.Model(model.input, model.get_layer("Gating_Network").output).predict(sample, verbose=0)
        sparse = keras_models.Model(model.input, model.get_layer("Sparse_Gate").output).predict(sample, verbose=0)
        self.assertEqual(sparse.shape, (4, 3))
        np.testing.assert_allclose(sparse.sum(axis=1), np.ones(4), atol=1e-5)
        self.assertTrue(np.all((sparse == 0).sum(axis=1) == 2))
        for row in range(4):
            chosen = int(np.argmax(router[row]))
            self.assertEqual(int(np.flatnonzero(sparse[row] > 0)[0]), chosen)
            self.assertAlmostEqual(float(sparse[row, chosen]), 1.0, places=5)

        wider = moe_lstm.build_moe_model(lookback=4, n_features=2, n_experts=4, top_k=2, aux_loss_weight=0)
        wider_sample = np.random.default_rng(1).normal(size=(3, 4, 2)).astype("float32")
        self.assertEqual(wider.predict(wider_sample, verbose=0).shape, (3, 1))
        wide_router = keras_models.Model(wider.input, wider.get_layer("Gating_Network").output).predict(
            wider_sample, verbose=0
        )
        wide_gate = keras_models.Model(wider.input, wider.get_layer("Sparse_Gate").output).predict(
            wider_sample, verbose=0
        )
        self.assertEqual(wide_gate.shape, (3, 4))
        self.assertTrue(np.all((wide_gate == 0).sum(axis=1) == 2))
        np.testing.assert_allclose(wide_gate.sum(axis=1), np.ones(3), atol=1e-5)
        for row in range(3):
            chosen = np.flatnonzero(wide_gate[row] > 0)
            expected = wide_router[row, chosen] / wide_router[row, chosen].sum()
            np.testing.assert_allclose(wide_gate[row, chosen], expected, atol=1e-5)

    def test_dense_gate_keeps_every_expert_and_aux_loss_is_sparse_only(self):
        dense = moe_lstm.build_moe_model(lookback=5, n_features=3, top_k=None)
        self.assertEqual(self._producer(dense.get_layer("Weighted_Sum").input[1]), "Gating_Network")
        with self.assertRaises(ValueError):
            dense.get_layer("Sparse_Gate")
        with self.assertRaises(ValueError):
            dense.get_layer("Load_Balance")
        sample = np.random.default_rng(2).normal(size=(2, 5, 3)).astype("float32")
        gate = keras_models.Model(dense.input, dense.get_layer("Gating_Network").output).predict(sample, verbose=0)
        self.assertEqual(dense.predict(sample, verbose=0).shape, (2, 1))
        self.assertTrue(np.all(gate > 0))
        np.testing.assert_allclose(gate.sum(axis=1), np.ones(2), atol=1e-5)
        with self.assertRaises(ValueError):
            moe_lstm.build_moe_model(lookback=5, n_features=3, top_k=None, aux_loss_weight=0.01)
        with self.assertRaises(ValueError):
            moe_lstm.build_moe_model(lookback=5, n_features=3, top_k=3)

        sparse = moe_lstm.build_moe_model(lookback=5, n_features=3, top_k=1)
        self.assertEqual(sparse.get_layer("Load_Balance").aux_weight, moe_lstm.AUX_LOSS_WEIGHT)
        history = sparse.fit(
            np.zeros((6, 5, 3), dtype="float32"),
            np.array([0, 1, 0, 1, 0, 1], dtype="float32"),
            epochs=1,
            verbose=0,
        )
        self.assertTrue(np.isfinite(history.history["loss"]).all())

    def test_early_stopping_uses_the_validation_tail_not_the_test_windows(self):
        frame = _synthetic_frame()
        split = moe_lstm.window_split(len(frame), moe_lstm.LOOKBACK)
        seen = {}
        original = keras_models.Model.fit

        def spy(self, x, y=None, **kwargs):
            seen["fit_rows"] = len(x)
            seen["val_rows"] = len(kwargs["validation_data"][0])
            seen["val_targets"] = np.asarray(kwargs["validation_data"][1]).copy()
            kwargs["epochs"] = 1
            return original(self, x, y, **kwargs)

        keras_models.Model.fit = spy
        try:
            result = moe_lstm.train_and_predict_moe(frame, ["A", "B", "C"], "Manual", epochs=1)
        finally:
            keras_models.Model.fit = original

        self.assertEqual(seen["fit_rows"], split.n_fit)
        self.assertEqual(seen["val_rows"], split.n_val)
        self.assertEqual(len(result["predictions"]), split.n_test)
        values = frame.loc[:, ["A", "B", "C"]].to_numpy(dtype=float)
        scaled = moe_lstm.scale_features(values, split.n_scale_rows)
        _, targets = moe_lstm.make_windows(scaled, frame["Target"].to_numpy(), moe_lstm.LOOKBACK)
        n_train = split.n_fit + split.n_val
        self.assertTrue(np.array_equal(seen["val_targets"], targets[split.n_fit : n_train].astype("float32")))
        self.assertFalse(np.array_equal(seen["val_targets"], targets[n_train:].astype("float32")))
        self.assertTrue(np.isfinite(result["accuracy"]))

    def test_main_trains_three_feature_sets_on_a_local_csv(self):
        import matplotlib

        matplotlib.use("Agg", force=True)
        rng = np.random.default_rng(2)
        closes = 100 + np.cumsum(rng.normal(0.05, 0.8, size=80))
        closes = np.abs(closes) + 20
        days = pd.bdate_range("2020-01-02", periods=len(closes))
        raw = pd.DataFrame(
            {
                "Date": [day.strftime("%m/%d/%Y") for day in days],
                "Close/Last": closes,
                "Open": closes,
                "High": closes + 0.4,
                "Low": closes - 0.4,
                "Note": "",
            }
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as handle:
            raw.to_csv(handle.name, index=False)
            csv_path = handle.name
        previous = os.environ.get("MOE_DATA_CSV")
        previous_oos = os.environ.get("MOE_OOS_CSV")
        previous_results = os.environ.get("MOE_RESULTS_DIR")
        oos_path = csv_path + ".oos.csv"
        results_dir = csv_path + ".results"
        os.environ["MOE_DATA_CSV"] = csv_path
        os.environ["MOE_OOS_CSV"] = oos_path
        os.environ["MOE_RESULTS_DIR"] = results_dir
        stdout = io.StringIO()
        saved_metrics = None
        equity = None
        held = None
        figure_names = (
            "close.png",
            "correlation.png",
            "confusion.png",
            "equity.png",
            "daily_returns.png",
            "metrics.csv",
            "equity.csv",
            "buy_and_hold.csv",
        )
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                with contextlib.redirect_stdout(stdout):
                    metrics = moe_lstm.main(epochs=1)
        finally:
            if previous is None:
                os.environ.pop("MOE_DATA_CSV", None)
            else:
                os.environ["MOE_DATA_CSV"] = previous
            if previous_oos is None:
                os.environ.pop("MOE_OOS_CSV", None)
            else:
                os.environ["MOE_OOS_CSV"] = previous_oos
            if previous_results is None:
                os.environ.pop("MOE_RESULTS_DIR", None)
            else:
                os.environ["MOE_RESULTS_DIR"] = previous_results
            os.remove(csv_path)
            present = {name: os.path.exists(os.path.join(results_dir, name)) for name in figure_names}
            if os.path.exists(os.path.join(results_dir, "metrics.csv")):
                saved_metrics = pd.read_csv(os.path.join(results_dir, "metrics.csv"))
            if os.path.exists(os.path.join(results_dir, "equity.csv")):
                equity = pd.read_csv(os.path.join(results_dir, "equity.csv"))
            if os.path.exists(os.path.join(results_dir, "buy_and_hold.csv")):
                held = pd.read_csv(os.path.join(results_dir, "buy_and_hold.csv"))
            shutil.rmtree(results_dir, ignore_errors=True)
            if os.path.exists(oos_path):
                saved = pd.read_csv(oos_path)
                os.remove(oos_path)
            else:
                saved = None

        self.assertIsNotNone(saved)
        self.assertEqual(list(saved.columns), ["Date", "Model", "Probability", "Prediction"])
        self.assertEqual(set(saved["Model"]), {"Manual", "KMeans", "SOM"})
        self.assertTrue(saved["Probability"].between(0, 1).all())
        self.assertGreater(saved["Probability"].nunique(), 1)

        self.assertEqual(list(metrics["Model"]), ["Manual", "KMeans", "SOM"])
        self.assertTrue(np.isfinite(metrics["Total Return"]).all())
        self.assertTrue(np.isfinite(metrics["Max Drawdown"]).all())
        self.assertTrue(metrics["Accuracy"].between(0, 1).all())
        text = stdout.getvalue()
        self.assertIn("模型性能对比", text)
        self.assertIn("K-Means Selected Features:", text)
        self.assertIn("SOM Selected Features:", text)
        self.assertNotIn("MOE 模型回测指标", text)
        self.assertFalse(any("FigureCanvasAgg" in str(item.message) for item in caught))
        missing = [name for name, exists in present.items() if not exists]
        self.assertEqual(missing, [])
        self.assertIsNotNone(saved_metrics)
        self.assertEqual(list(saved_metrics["Model"]), ["Manual", "KMeans", "SOM"])
        self.assertIsNotNone(equity)
        self.assertEqual(list(equity.columns), ["Date", "Manual", "KMeans", "SOM", "Buy & Hold"])
        self.assertIsNotNone(held)
        self.assertEqual(list(held["Model"]), ["Buy & Hold"])
        self.assertTrue(np.isfinite(held["Total Return"]).all())


if __name__ == "__main__":
    unittest.main()
