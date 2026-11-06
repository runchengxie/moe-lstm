import os
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import moe_lstm


def _price_frame(closes, dates=None, extra=None) -> pd.DataFrame:
    closes = [float(value) for value in closes]
    if dates is None:
        days = pd.bdate_range("2020-01-02", periods=len(closes))
        dates = [day.strftime("%m/%d/%Y") for day in days]
    frame = pd.DataFrame(
        {
            "Date": list(dates),
            "Close/Last": closes,
            "Open": closes,
            "High": [value + 0.5 for value in closes],
            "Low": [max(value - 0.5, 0.1) for value in closes],
        }
    )
    if extra:
        for key, value in extra.items():
            frame[key] = value
    return frame


def _write_csv(frame: pd.DataFrame) -> str:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as handle:
        frame.to_csv(handle.name, index=False)
        return handle.name


def _load(frame: pd.DataFrame) -> pd.DataFrame:
    path = _write_csv(frame)
    try:
        return moe_lstm.load_price_csv(path)
    finally:
        os.remove(path)


def _varied_closes(n: int) -> np.ndarray:
    rng = np.random.default_rng(1)
    close = 100 + np.cumsum(rng.normal(0, 0.4, size=n))
    return np.abs(close) + 10


class ContractTests(unittest.TestCase):
    def test_constants_match_the_documented_study(self):
        self.assertEqual(moe_lstm.THRESHOLD, 0.002)
        self.assertEqual(moe_lstm.LOOKBACK, 5)
        self.assertEqual(moe_lstm.N_CLUSTERS, 5)
        self.assertEqual(moe_lstm.TRAIN_FRACTION, 0.8)
        self.assertEqual(moe_lstm.VAL_FRACTION, 0.2)
        self.assertEqual(moe_lstm.BACKTEST_FEE, 0.0005)
        self.assertEqual(moe_lstm.EPOCHS, 50)
        self.assertEqual(moe_lstm.BATCH_SIZE, 16)
        self.assertEqual(moe_lstm.PATIENCE, 5)
        self.assertEqual(moe_lstm.ANNUALIZATION_DAYS, 252)
        self.assertEqual(moe_lstm.PREDICTION_THRESHOLD, 0.5)
        self.assertEqual(
            moe_lstm.MANUAL_FEATURE_COLUMNS,
            (
                "Close/Last",
                "MA5",
                "MA10",
                "EMA5",
                "EMA10",
                "RSI",
                "BB_upper",
                "BB_lower",
                "MACD",
                "Signal_line",
                "Daily_Return",
                "Volatility",
                "Open",
                "High",
                "Low",
            ),
        )

    def test_default_data_path_is_the_environment_override(self):
        previous = os.environ.pop("MOE_DATA_CSV", None)
        try:
            self.assertEqual(moe_lstm.resolve_data_path(), moe_lstm.DEFAULT_DATA_URL)
            self.assertTrue(moe_lstm.DEFAULT_DATA_URL.endswith("historical_data.csv"))
            os.environ["MOE_DATA_CSV"] = "/tmp/bars.csv"
            self.assertEqual(moe_lstm.resolve_data_path(), "/tmp/bars.csv")
        finally:
            if previous is None:
                os.environ.pop("MOE_DATA_CSV", None)
            else:
                os.environ["MOE_DATA_CSV"] = previous

    def test_importing_the_module_does_not_train(self):
        self.assertTrue(callable(moe_lstm.main))
        self.assertNotIn("model", moe_lstm.__dict__)

    def test_moe_epochs_overrides_the_default_at_startup(self):
        previous = os.environ.get("MOE_EPOCHS")
        try:
            os.environ.pop("MOE_EPOCHS", None)
            self.assertEqual(moe_lstm.resolve_epochs(), moe_lstm.EPOCHS)
            os.environ["MOE_EPOCHS"] = "1"
            self.assertEqual(moe_lstm.resolve_epochs(), 1)
            self.assertEqual(moe_lstm.resolve_epochs(3), 3)
            os.environ["MOE_EPOCHS"] = "0"
            with self.assertRaises(SystemExit):
                moe_lstm.resolve_epochs()
            os.environ["MOE_EPOCHS"] = "nope"
            with self.assertRaises(SystemExit):
                moe_lstm.resolve_epochs()
        finally:
            if previous is None:
                os.environ.pop("MOE_EPOCHS", None)
            else:
                os.environ["MOE_EPOCHS"] = previous


class LoadTests(unittest.TestCase):
    def test_missing_file_tells_the_user_which_variable_to_set(self):
        with self.assertRaises(SystemExit) as caught:
            moe_lstm.load_price_csv("/no/such/bars.csv")
        self.assertIn("MOE_DATA_CSV", str(caught.exception))

    def test_missing_column_names_the_contract(self):
        path = _write_csv(pd.DataFrame({"Date": ["01/02/2020"], "Close/Last": [10.0]}))
        try:
            with self.assertRaises(SystemExit) as caught:
                moe_lstm.load_price_csv(path)
        finally:
            os.remove(path)
        message = str(caught.exception)
        self.assertIn("Open", message)
        self.assertIn("High", message)
        self.assertIn("Low", message)

    def test_iso_dates_and_currency_text_are_rejected(self):
        path = _write_csv(_price_frame([100, 101, 102], dates=["2020-01-02", "2020-01-03", "2020-01-06"]))
        try:
            with self.assertRaises(SystemExit) as caught:
                moe_lstm.load_price_csv(path)
        finally:
            os.remove(path)
        self.assertIn("%m/%d/%Y", str(caught.exception))

        priced = _price_frame([100, 101, 102])
        priced["Close/Last"] = ["$100", "$101", "$102"]
        path = _write_csv(priced)
        try:
            with self.assertRaises(SystemExit) as caught:
                moe_lstm.load_price_csv(path)
        finally:
            os.remove(path)
        self.assertIn("Close/Last", str(caught.exception))

    def test_duplicate_dates_and_non_positive_closes_are_rejected(self):
        path = _write_csv(_price_frame([100, 101], dates=["01/02/2020", "01/02/2020"]))
        try:
            with self.assertRaises(SystemExit) as caught:
                moe_lstm.load_price_csv(path)
        finally:
            os.remove(path)
        self.assertIn("duplicate", str(caught.exception))

        path = _write_csv(_price_frame([100, 0, 102]))
        try:
            with self.assertRaises(SystemExit) as caught:
                moe_lstm.load_price_csv(path)
        finally:
            os.remove(path)
        self.assertIn("positive", str(caught.exception))

    def test_unpadded_month_and_day_are_accepted(self):
        loaded = _load(_price_frame([100, 101, 102], dates=["1/2/2020", "1/3/2020", "1/6/2020"]))
        self.assertEqual(
            list(loaded["Date"].dt.strftime("%Y-%m-%d")),
            ["2020-01-02", "2020-01-03", "2020-01-06"],
        )

    def test_rows_are_sorted_and_extra_columns_are_kept(self):
        loaded = _load(
            _price_frame(
                [101, 100, 102],
                dates=["01/03/2020", "01/02/2020", "01/06/2020"],
                extra={"Note": ["a", None, "c"]},
            )
        )
        self.assertEqual(list(loaded["Close/Last"]), [100, 101, 102])
        self.assertIn("Note", loaded.columns)
        self.assertTrue(pd.isna(loaded["Note"].iloc[0]))

    def test_smoke_fixture_matches_the_csv_contract(self):
        path = ROOT / "tests" / "fixtures" / "tiny_bars.csv"
        loaded = moe_lstm.load_price_csv(str(path))
        self.assertEqual(len(loaded), 120)
        features = moe_lstm.build_feature_frame(loaded)
        split = moe_lstm.window_split(len(features))
        self.assertGreaterEqual(split.n_fit, 1)
        self.assertGreaterEqual(split.n_test, 1)
        self.assertIsNone(moe_lstm.session_gap_warning(features["Date"]))

    def test_study_loader_prefers_hive_minutes_and_still_validates_csv(self):
        from tests.test_hive_daily_bars import _minute_frame, _write_year

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "ignored.csv"
            csv_path.write_text(
                "Date,Open,High,Low,Close/Last\nnot-a-date,1,1,1,1\n",
                encoding="utf-8",
            )
            _write_year(
                root,
                "ZURA",
                "only-hash",
                "2024",
                _minute_frame(
                    [
                        {
                            "Date": "20240102",
                            "TimeBarStart": "09:31",
                            "AuditSession": "regular",
                            "FirstTradePrice": "2",
                            "HighTradePrice": "3",
                            "LowTradePrice": "1",
                            "LastTradePrice": "2.5",
                            "Volume": 4,
                        }
                    ]
                ),
            )
            loaded = moe_lstm.load_study_prices(
                {
                    "MOE_DATA_PARQUET": str(root),
                    "MOE_SYMBOL": "ZURA",
                    "MOE_DATA_CSV": str(csv_path),
                }
            )
            self.assertEqual(loaded.loc[0, "Open"], 2.0)
            self.assertEqual(float(loaded.loc[0, "Close/Last"]), 2.5)
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(loaded["Date"]))

            with self.assertRaises(SystemExit) as caught:
                moe_lstm.load_study_prices({"MOE_DATA_CSV": str(csv_path)})
            self.assertIn("%m/%d/%Y", str(caught.exception))

    def test_header_only_file_is_rejected(self):
        path = _write_csv(pd.DataFrame(columns=["Date", "Close/Last", "Open", "High", "Low"]))
        try:
            with self.assertRaises(SystemExit) as caught:
                moe_lstm.load_price_csv(path)
        finally:
            os.remove(path)
        self.assertIn("no rows", str(caught.exception))


class FeatureTests(unittest.TestCase):
    def test_label_boundary_is_strictly_above_the_threshold(self):
        labels = moe_lstm.label_directions(pd.Series([0.0019, 0.002, 0.0020000001]))
        self.assertEqual(list(labels), [0, 0, 1])
        with self.assertRaises(ValueError):
            moe_lstm.label_directions(pd.Series([0.01, np.nan]))

    def test_flat_prices_keep_a_neutral_rsi_and_are_not_deleted(self):
        features = moe_lstm.build_feature_frame(_load(_price_frame([100.0] * 40)))
        self.assertEqual(len(features), 20)
        self.assertTrue((features["RSI"] == 50).all())
        self.assertTrue((features["Target"] == 0).all())
        self.assertTrue(np.isfinite(features["Tomorrow_Change"]).all())

    def test_minimum_history_is_28_sessions(self):
        short = moe_lstm.build_feature_frame(_load(_price_frame(_varied_closes(27))))
        with self.assertRaises(ValueError):
            moe_lstm.window_split(len(short))
        features = moe_lstm.build_feature_frame(_load(_price_frame(_varied_closes(28))))
        split = moe_lstm.window_split(len(features))
        self.assertEqual(len(features), 8)
        self.assertEqual(split, moe_lstm.WindowSplit(1, 1, 1, 5))

    def test_forward_return_is_the_next_close_and_extra_nans_do_not_drop_rows(self):
        closes = _varied_closes(40)
        closes[18] = 100.0
        closes[19] = 150.0
        closes[20] = 151.5
        loaded = _load(_price_frame(closes))
        plain = moe_lstm.build_feature_frame(loaded)
        dirty = loaded.copy()
        dirty["Note"] = np.nan
        with_extra = moe_lstm.build_feature_frame(dirty)
        self.assertEqual(len(with_extra), len(plain))
        self.assertTrue(with_extra["Target"].equals(plain["Target"]))
        self.assertEqual(len(plain), 20)
        self.assertAlmostEqual(plain["Daily_Return"].iloc[0], 0.5)
        self.assertAlmostEqual(plain["Tomorrow_Change"].iloc[0], 0.01)
        self.assertTrue(
            np.allclose(
                plain["Tomorrow_Change"].iloc[:-1].to_numpy(),
                plain["Daily_Return"].iloc[1:].to_numpy(),
            )
        )
        result = moe_lstm.backtest([1], plain.iloc[:1], "Manual", fee=0)
        self.assertAlmostEqual(result["Total Return"], 0.01)

    def test_rising_window_rsi_is_100(self):
        closes = [100 * (1.01**i) for i in range(40)]
        features = moe_lstm.build_feature_frame(_load(_price_frame(closes)))
        self.assertTrue((features["RSI"] == 100).all())
        self.assertTrue((features["Target"] == 1).all())


class SplitAndBacktestTests(unittest.TestCase):
    def test_split_counts_and_scaler_stop_before_the_test_windows(self):
        split = moe_lstm.window_split(100, lookback=5)
        self.assertEqual(split, moe_lstm.WindowSplit(61, 15, 19, 65))
        first_test_window = split.n_fit + split.n_val
        self.assertLessEqual(split.n_scale_rows, first_test_window)
        rows = moe_lstm.prediction_rows(
            pd.DataFrame({"Tomorrow_Change": np.arange(100)}),
            lookback=5,
            n_test=split.n_test,
        )
        self.assertEqual(list(rows["Tomorrow_Change"]), list(range(81, 100)))

    def test_scaler_and_cluster_matrix_ignore_the_test_tail(self):
        values = np.array([[0.0], [10.0], [10.0], [1000.0]])
        scaled = moe_lstm.scale_features(values, 3)
        self.assertAlmostEqual(scaled[1, 0], 1.0)
        self.assertAlmostEqual(scaled[3, 0], 100.0)

        base = np.arange(20, dtype=float).reshape(10, 2)
        altered = base.copy()
        altered[7:] = 999.0
        self.assertTrue(
            np.allclose(moe_lstm.cluster_matrix(base, 7), moe_lstm.cluster_matrix(altered, 7))
        )

    def test_feature_selection_is_deterministic_and_stays_inside_the_names(self):
        rows = 12
        matrix = np.zeros((rows, 4))
        matrix[:, 0] = np.linspace(0, 1, rows)
        matrix[:, 1] = matrix[:, 0] + 0.01
        matrix[:, 2] = np.linspace(1, 0, rows)
        matrix[:, 3] = matrix[:, 2] + 0.01
        names = ["a", "b", "c", "d"]
        first = moe_lstm.select_kmeans_features(matrix, names, n_clusters=2)
        second = moe_lstm.select_kmeans_features(matrix, names, n_clusters=2)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 2)
        self.assertTrue(set(first).issubset(names))
        som_first = moe_lstm.select_som_features(matrix, names)
        som_second = moe_lstm.select_som_features(matrix, names)
        self.assertEqual(som_first, som_second)
        self.assertTrue(set(som_first).issubset(names))
        self.assertGreaterEqual(len(som_first), 1)

    def test_backtest_earns_the_forward_return_and_charges_turnover(self):
        frame = pd.DataFrame(
            {
                "Tomorrow_Change": [0.01, 0.02, -0.03, 0.04],
                "Daily_Return": [0.50, 0.50, 0.50, 0.50],
            }
        )
        held = moe_lstm.backtest([1, 1, 1, 1], frame, "Manual", fee=0.0005)
        strategy = np.array([0.01 - 0.0005, 0.02, -0.03, 0.04])
        self.assertAlmostEqual(held["Total Return"], float(np.prod(1 + strategy) - 1))
        every_bar = float(np.prod(1 + (frame["Tomorrow_Change"].to_numpy() - 0.0005)) - 1)
        self.assertNotAlmostEqual(held["Total Return"], every_bar)

        flipped = moe_lstm.backtest([1, 1, 0, 0], frame, "Manual", fee=0.001)
        flat_strategy = np.array(
            [
                1 * 0.01 - 0.001,
                1 * 0.02,
                0 * -0.03 - 0.001,
                0 * 0.04,
            ]
        )
        self.assertAlmostEqual(flipped["Total Return"], float(np.prod(1 + flat_strategy) - 1))
        stayed_out = moe_lstm.backtest([0, 0, 0, 0], frame, "Manual", fee=0.001)
        self.assertEqual(stayed_out["Total Return"], 0.0)
        self.assertEqual(stayed_out["Max Drawdown"], 0.0)

    def test_drawdown_includes_the_starting_equity(self):
        down = pd.DataFrame({"Tomorrow_Change": [-0.1, -0.1]})
        result = moe_lstm.backtest([1, 1], down, "Manual", fee=0)
        self.assertAlmostEqual(result["Total Return"], 0.81 - 1)
        self.assertAlmostEqual(result["Max Drawdown"], 0.81 - 1)

        up_then_down = pd.DataFrame({"Tomorrow_Change": [0.1, -0.1]})
        peaked = moe_lstm.backtest([1, 1], up_then_down, "Manual", fee=0)
        self.assertAlmostEqual(peaked["Max Drawdown"], (0.99 - 1.1) / 1.1)

        opened = moe_lstm.backtest(
            [1], pd.DataFrame({"Tomorrow_Change": [0.0]}), "Manual", fee=0.0005
        )
        self.assertAlmostEqual(opened["Total Return"], -0.0005)
        self.assertAlmostEqual(opened["Max Drawdown"], -0.0005)

        flat = pd.DataFrame({"Tomorrow_Change": [0.0, 0.0, 0.0]})
        quiet = moe_lstm.backtest([1, 1, 1], flat, "Manual", fee=0)
        self.assertEqual(quiet["Total Return"], 0.0)
        self.assertEqual(quiet["Max Drawdown"], 0.0)
        self.assertTrue(np.isnan(quiet["Sharpe Ratio"]))

    def test_oos_table_keeps_soft_probabilities_and_dates(self):
        dates = pd.to_datetime(["2020-01-02", "2020-01-03"])
        table = moe_lstm.oos_probability_frame(dates, "Manual", [0.2, 0.8], [0, 1])
        self.assertEqual(list(table["Model"]), ["Manual", "Manual"])
        self.assertAlmostEqual(float(table["Probability"].iloc[0]), 0.2)
        self.assertEqual(list(table["Prediction"]), [0, 1])
        self.assertEqual(table["Date"].iloc[1], dates[1])
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "oos.csv")
            moe_lstm.write_oos_probabilities([table], path)
            loaded = pd.read_csv(path)
        self.assertEqual(list(loaded.columns), ["Date", "Model", "Probability", "Prediction"])
        self.assertAlmostEqual(float(loaded["Probability"].iloc[1]), 0.8)

    def test_label_window_starts_after_the_feature_cutoff(self):
        closes = 100 + np.arange(40, dtype=float)
        frame = moe_lstm.build_feature_frame(_load(_price_frame(closes)))
        close = frame["Close/Last"].to_numpy()
        forward = close[1:] / close[:-1] - 1
        self.assertTrue(np.allclose(frame["Tomorrow_Change"].iloc[:-1].to_numpy(), forward))
        labels = moe_lstm.label_directions(pd.Series([0.002, 0.001, -0.01, 0.0020000001]))
        self.assertEqual(list(labels), [0, 0, 0, 1])
        lookback = moe_lstm.LOOKBACK
        windows, targets = moe_lstm.make_windows(close.reshape(-1, 1), frame["Target"].to_numpy(), lookback)
        self.assertEqual(windows[0, -1, 0], close[lookback - 1])
        self.assertNotEqual(windows[0, -1, 0], close[lookback])
        self.assertEqual(targets[0], frame["Target"].iloc[lookback])
        split = moe_lstm.window_split(len(frame), lookback)
        last_fit_feature = split.n_fit - 1 + lookback - 1
        self.assertEqual(split.n_scale_rows, last_fit_feature + 1)
        self.assertEqual(last_fit_feature + 1, split.n_scale_rows)

    def test_backtest_rejects_bad_inputs(self):
        frame = pd.DataFrame({"Tomorrow_Change": [0.01, 0.02], "Daily_Return": [0.5, 0.5]})
        with self.assertRaises(ValueError):
            moe_lstm.backtest([1], frame, "Manual")
        with self.assertRaises(ValueError):
            moe_lstm.backtest([1, 2], frame, "Manual")
        with self.assertRaises(ValueError):
            moe_lstm.backtest([1, 1], frame.drop(columns=["Tomorrow_Change"]), "Manual")

    def test_single_class_scores_do_not_raise(self):
        scores = moe_lstm.classification_scores([0, 0, 0], [0.2, 0.3, 0.1], [0, 0, 0])
        self.assertEqual(scores["accuracy"], 1.0)
        self.assertEqual(scores["precision"], 0.0)
        self.assertTrue(np.isnan(scores["auc_roc"]))
        perfect = moe_lstm.classification_scores(
            [0, 1, 1, 0], [0.1, 0.8, 0.7, 0.4], [0, 1, 1, 0]
        )
        self.assertEqual(perfect["accuracy"], 1.0)
        self.assertGreater(perfect["auc_roc"], 0.99)

    def test_windows_use_the_label_on_the_row_after_the_lookback(self):
        scaled = np.arange(20, dtype=float).reshape(10, 2)
        labels = np.arange(10)
        windows, targets = moe_lstm.make_windows(scaled, labels, lookback=5)
        self.assertEqual(windows.shape, (5, 5, 2))
        self.assertTrue(np.array_equal(targets, np.arange(5, 10)))
        self.assertTrue(np.array_equal(windows[0, :, 0], np.arange(0, 10, 2)))

    def test_session_gap_warning_allows_weekends_and_flags_monthly_bars(self):
        daily = pd.bdate_range("2020-01-01", periods=30)
        self.assertIsNone(moe_lstm.session_gap_warning(pd.Series(daily)))
        monthly = pd.date_range("2020-01-01", periods=6, freq="MS")
        warning = moe_lstm.session_gap_warning(pd.Series(monthly))
        self.assertIsNotNone(warning)
        self.assertIn("sqrt(252)", warning)
        self.assertIn("median date gap", warning)

    def test_buy_and_hold_uses_the_forward_return(self):
        forward = pd.Series([0.01, -0.02, 0.03])
        equity = moe_lstm.buy_and_hold_equity(forward)
        self.assertTrue(np.allclose(equity.to_numpy(), np.cumprod(1 + forward.to_numpy())))


if __name__ == "__main__":
    unittest.main()
