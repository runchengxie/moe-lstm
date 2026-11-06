import contextlib
import io
import os
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
        os.environ["MOE_DATA_CSV"] = csv_path
        stdout = io.StringIO()
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
            os.remove(csv_path)

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


if __name__ == "__main__":
    unittest.main()
