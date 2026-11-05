"""Synthetic Hive minute bars aggregated to the daily OHLCV columns.

No market data is stored here. Prices are made up so the open/high/low/close
rules can be checked without a vendor sample.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from price_data import (
    aggregate_regular_minutes,
    finalize_price_dates,
    load_price_frame,
)


def _write_year(root: Path, symbol: str, security: str, year: str, frame: pd.DataFrame) -> None:
    directory = (
        root
        / "parquet"
        / f"symbol={symbol}"
        / f"security={security}"
        / f"year={year}"
    )
    directory.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(directory / "data.parquet", index=False)
    # Hive jobs often drop a marker next to the part file. It must be ignored.
    (directory / "_SUCCESS").write_text("", encoding="utf-8")


def _minute_frame(rows: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    for column in frame.columns:
        if column != "Volume":
            frame[column] = frame[column].astype("string")
    return frame


class HiveDailyBarsTest(unittest.TestCase):
    def _build_tree(self, root: Path) -> None:
        # Written out of clock order. Open must follow TimeBarStart, not file order.
        traded_day = _minute_frame(
            [
                {
                    "Date": "20240102",
                    "TimeBarStart": "10:00",
                    "AuditSession": "regular",
                    "FirstTradePrice": "11",
                    "HighTradePrice": "12",
                    "LowTradePrice": "10.5",
                    "LastTradePrice": "11.5",
                    "Volume": 50,
                },
                {
                    "Date": "20240102",
                    "TimeBarStart": "09:31",
                    "AuditSession": "regular",
                    "FirstTradePrice": "10",
                    "HighTradePrice": "10.5",
                    "LowTradePrice": "9.5",
                    "LastTradePrice": "10",
                    "Volume": 100,
                },
                {
                    "Date": "20240102",
                    "TimeBarStart": "09:45",
                    "AuditSession": "regular",
                    "FirstTradePrice": "10.5",
                    "HighTradePrice": "11",
                    "LowTradePrice": "10",
                    "LastTradePrice": "11",
                    "Volume": 25,
                },
                {
                    "Date": "20240102",
                    "TimeBarStart": "09:32",
                    "AuditSession": "regular",
                    "FirstTradePrice": "",
                    "HighTradePrice": "",
                    "LowTradePrice": "",
                    "LastTradePrice": "",
                    "Volume": 1000,
                },
                {
                    "Date": "20240102",
                    "TimeBarStart": "09:55",
                    "AuditSession": "regular",
                    "FirstTradePrice": "20",
                    "HighTradePrice": "",
                    "LowTradePrice": "19",
                    "LastTradePrice": "20",
                    "Volume": 999,
                },
                {
                    "Date": "20240102",
                    "TimeBarStart": "08:00",
                    "AuditSession": "pre",
                    "FirstTradePrice": "1",
                    "HighTradePrice": "100",
                    "LowTradePrice": "0.5",
                    "LastTradePrice": "1",
                    "Volume": 5000,
                },
                {
                    "Date": "20240102",
                    "TimeBarStart": "16:01",
                    "AuditSession": "post",
                    "FirstTradePrice": "50",
                    "HighTradePrice": "80",
                    "LowTradePrice": "40",
                    "LastTradePrice": "70",
                    "Volume": 7000,
                },
                {
                    "Date": "20240102",
                    "TimeBarStart": "11:00",
                    "AuditSession": "Regular",
                    "FirstTradePrice": "3",
                    "HighTradePrice": "1000",
                    "LowTradePrice": "1",
                    "LastTradePrice": "3",
                    "Volume": 8000,
                },
                {
                    "Date": "20240103",
                    "TimeBarStart": "09:31",
                    "AuditSession": " regular ",
                    "FirstTradePrice": "7",
                    "HighTradePrice": "8",
                    "LowTradePrice": "6",
                    "LastTradePrice": "7.5",
                    "Volume": 3,
                },
            ]
        )
        prior_year = _minute_frame(
            [
                {
                    "Date": "20231229",
                    "TimeBarStart": "09:31",
                    "AuditSession": "regular",
                    "FirstTradePrice": "5",
                    "HighTradePrice": "6",
                    "LowTradePrice": "4",
                    "LastTradePrice": "5.5",
                    "Volume": 10,
                }
            ]
        )
        other_symbol = _minute_frame(
            [
                {
                    "Date": "20240102",
                    "TimeBarStart": "09:31",
                    "AuditSession": "regular",
                    "FirstTradePrice": "10000",
                    "HighTradePrice": "10000",
                    "LowTradePrice": "10000",
                    "LastTradePrice": "10000",
                    "Volume": 1,
                }
            ]
        )
        other_security = _minute_frame(
            [
                {
                    "Date": "20240102",
                    "TimeBarStart": "09:31",
                    "AuditSession": "regular",
                    "FirstTradePrice": "999",
                    "HighTradePrice": "999",
                    "LowTradePrice": "999",
                    "LastTradePrice": "999",
                    "Volume": 1,
                }
            ]
        )
        _write_year(root, "ZURA", "hash-a", "2024", traded_day)
        _write_year(root, "ZURA", "hash-a", "2023", prior_year)
        _write_year(root, "OTHER", "hash-z", "2024", other_symbol)
        _write_year(root, "ZURA", "hash-b", "2024", other_security)

    def test_hive_tree_aggregates_regular_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._build_tree(root)
            loaded = load_price_frame(
                {
                    "MOE_DATA_PARQUET": str(root),
                    "MOE_SYMBOL": "ZURA",
                    "MOE_SECURITY": "hash-a",
                    "MOE_DATA_CSV": str(root / "ignored.csv"),
                }
            )
            dated = finalize_price_dates(loaded)
            expected = pd.DataFrame(
                {
                    "Date": pd.to_datetime(["2023-12-29", "2024-01-02", "2024-01-03"]),
                    "Open": [5.0, 10.0, 7.0],
                    "High": [6.0, 12.0, 8.0],
                    "Low": [4.0, 9.5, 6.0],
                    "Close/Last": [5.5, 11.5, 7.5],
                    "Volume": [10.0, 175.0, 3.0],
                }
            )
            pd.testing.assert_frame_equal(
                dated.reset_index(drop=True),
                expected,
                check_freq=False,
            )

            from_parquet_dir = load_price_frame(
                {
                    "MOE_DATA_PARQUET": str(root / "parquet"),
                    "MOE_SYMBOL": "ZURA",
                    "MOE_SECURITY": "hash-a",
                }
            )
            pd.testing.assert_frame_equal(
                from_parquet_dir.reset_index(drop=True),
                expected,
                check_freq=False,
            )

    def test_multiple_securities_require_moe_security(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._build_tree(root)
            env = {"MOE_DATA_PARQUET": str(root), "MOE_SYMBOL": "ZURA"}
            with self.assertRaises(SystemExit) as ctx:
                load_price_frame(env)
            self.assertIn("MOE_SECURITY", str(ctx.exception))

            with self.assertRaises(SystemExit) as missing:
                load_price_frame({**env, "MOE_SECURITY": "missing-hash"})
            self.assertIn("missing-hash", str(missing.exception))

    def test_single_security_is_selected_without_moe_security(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            only = _minute_frame(
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
            )
            _write_year(root, "ZURA", "only-hash", "2024", only)
            loaded = load_price_frame(
                {"MOE_DATA_PARQUET": str(root), "MOE_SYMBOL": "ZURA"}
            )
            self.assertEqual(loaded.loc[0, "Open"], 2.0)
            self.assertEqual(loaded.loc[0, "Close/Last"], 2.5)
            self.assertEqual(loaded.loc[0, "Volume"], 4.0)

    def test_symbol_partition_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._build_tree(root)
            with self.assertRaises(SystemExit) as ctx:
                load_price_frame(
                    {"MOE_DATA_PARQUET": str(root), "MOE_SYMBOL": "MISSING"}
                )
            self.assertIn("MISSING", str(ctx.exception))

    def test_parquet_root_requires_symbol(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            load_price_frame({"MOE_DATA_PARQUET": "/tmp/does-not-matter"})
        self.assertIn("MOE_SYMBOL", str(ctx.exception))

    def test_csv_fallback_keeps_us_date_strings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "bars.csv"
            csv_path.write_text(
                "Date,Open,High,Low,Close/Last\n"
                "01/03/2024,3,4,2,3.5\n"
                "01/02/2024,1,2,0.5,1.5\n",
                encoding="utf-8",
            )
            loaded = load_price_frame(
                {"MOE_DATA_PARQUET": "  ", "MOE_DATA_CSV": str(csv_path)}
            )
            self.assertEqual(list(loaded["Date"]), ["01/03/2024", "01/02/2024"])
            self.assertFalse(pd.api.types.is_datetime64_any_dtype(loaded["Date"]))
            dated = finalize_price_dates(loaded)
            self.assertEqual(
                list(dated["Date"]),
                [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-03")],
            )
            self.assertEqual(list(dated["Close/Last"]), [1.5, 3.5])

            missing = Path(tmp) / "missing.csv"
            with self.assertRaises(SystemExit) as ctx:
                load_price_frame({"MOE_DATA_CSV": str(missing)})
            message = str(ctx.exception)
            self.assertIn("MOE_DATA_CSV", message)
            self.assertIn("%m/%d/%Y", message)

    def test_blank_strings_decimals_and_trade_time_order(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "Date": "20240603",
                    "FirstTradeTime": "10:00:00.100000000",
                    "AuditSession": "regular",
                    "FirstTradePrice": Decimal("4"),
                    "HighTradePrice": Decimal("4.5"),
                    "LowTradePrice": Decimal("3.5"),
                    "LastTradePrice": Decimal("4"),
                    "Volume": "",
                },
                {
                    "Date": "20240603",
                    "FirstTradeTime": "09:31:00",
                    "AuditSession": "regular",
                    "FirstTradePrice": Decimal("3"),
                    "HighTradePrice": Decimal("3.5"),
                    "LowTradePrice": Decimal("2.5"),
                    "LastTradePrice": Decimal("3"),
                    "Volume": Decimal("8"),
                },
                {
                    "Date": "20240603",
                    "FirstTradeTime": "15:59:00",
                    "AuditSession": "regular",
                    "FirstTradePrice": " ",
                    "HighTradePrice": " ",
                    "LowTradePrice": " ",
                    "LastTradePrice": " ",
                    "Volume": "50",
                },
            ]
        )
        daily = aggregate_regular_minutes(frame)
        self.assertEqual(daily.loc[0, "Open"], 3.0)
        self.assertEqual(daily.loc[0, "High"], 4.5)
        self.assertEqual(daily.loc[0, "Low"], 2.5)
        self.assertEqual(daily.loc[0, "Close/Last"], 4.0)
        self.assertEqual(daily.loc[0, "Volume"], 8.0)

    def test_no_regular_session_is_an_error(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "Date": "20240102",
                    "TimeBarStart": "08:00",
                    "AuditSession": "pre",
                    "FirstTradePrice": 1,
                    "HighTradePrice": 1,
                    "LowTradePrice": 1,
                    "LastTradePrice": 1,
                    "Volume": 1,
                }
            ]
        )
        with self.assertRaises(SystemExit) as ctx:
            aggregate_regular_minutes(frame)
        self.assertIn("regular", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
