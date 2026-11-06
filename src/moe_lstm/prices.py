"""Load the daily OHLCV frame the study trains on.

Primary source is a Hive tree of processed US-equity minute bars:

    parquet/symbol=SYMBOL/security=HASH/year=YYYY/data.parquet

`MOE_DATA_PARQUET` is that dataset root (or the `parquet/` directory itself).
`MOE_SYMBOL` picks the ticker. `MOE_SECURITY` is required only when several
security hashes share the ticker. Minutes with `AuditSession == regular` and
non-blank trade prices are aggregated to one row per calendar date.

If `MOE_DATA_PARQUET` is unset, `MOE_DATA_CSV` (or the legacy default URL) is
read unchanged so a small CSV smoke file still runs.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_DATA_URL = (
    "https://raw.githubusercontent.com/runchengxie/quant_practice_3/"
    "refs/heads/main/historical_data.csv"
)

REGULAR_SESSION = "regular"
PRICE_COLUMNS = (
    "FirstTradePrice",
    "HighTradePrice",
    "LowTradePrice",
    "LastTradePrice",
)
# TimeBarStart is the minute-bar clock (HH:MM). FirstTradeTime is the fallback
# when a file only carries the trade timestamp.
TIME_COLUMNS = ("TimeBarStart", "FirstTradeTime", "OpenBarTime")
DAILY_COLUMNS = ["Date", "Open", "High", "Low", "Close/Last", "Volume"]

_CLOCK = re.compile(r"(\d{1,2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?")


def load_price_frame(env: Mapping[str, str] | None = None) -> pd.DataFrame:
    """Return daily bars from Hive minute Parquet, or from CSV if that is unset."""
    if env is None:
        env = os.environ
    parquet_root = str(env.get("MOE_DATA_PARQUET", "")).strip()
    if parquet_root:
        symbol = str(env.get("MOE_SYMBOL", "")).strip()
        if not symbol:
            raise SystemExit(
                "MOE_DATA_PARQUET is set but MOE_SYMBOL is empty. "
                "Set MOE_SYMBOL to the Hive ticker (the symbol= partition)."
            )
        security = str(env.get("MOE_SECURITY", "")).strip() or None
        daily, chosen, years = load_hive_daily_bars(parquet_root, symbol, security)
        year_text = ", ".join(years) if years else "no year= partition"
        bar_word = "daily bar" if len(daily) == 1 else "daily bars"
        print(
            f"Loaded {len(daily)} {bar_word} for symbol {symbol} "
            f"(security {chosen}; years {year_text}) from {parquet_root}."
        )
        return daily
    if "MOE_DATA_CSV" in env:
        csv_path = env["MOE_DATA_CSV"]
    else:
        csv_path = DEFAULT_DATA_URL
    return load_csv_bars(csv_path)


def load_csv_bars(path: str) -> pd.DataFrame:
    """Read a legacy daily CSV. Date stays a `%m/%d/%Y` string for the caller."""
    try:
        return pd.read_csv(path)
    except Exception as exc:
        raise SystemExit(
            f"Could not read price data from {path!r} ({exc}). "
            "Set MOE_DATA_CSV to a local CSV with columns "
            "Date (%m/%d/%Y), Close/Last, Open, High, and Low. "
            "Price columns must be numeric."
        ) from exc


def finalize_price_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Parse CSV dates as `%m/%d/%Y`. Leave Parquet dates, already datetimes, alone."""
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        out = df.copy()
        out["Date"] = pd.to_datetime(out["Date"], format="%m/%d/%Y")
        return out.sort_values(by="Date")
    return df.sort_values(by="Date")


def load_hive_daily_bars(
    dataset_root: str | os.PathLike[str],
    symbol: str,
    security: str | None = None,
) -> tuple[pd.DataFrame, str, list[str]]:
    """Read every year for one symbol and return daily OHLCV, security, and years."""
    _check_token("MOE_SYMBOL", symbol)
    if security is not None:
        _check_token("MOE_SECURITY", security)
    root = Path(dataset_root).expanduser()
    if not root.exists():
        raise SystemExit(f"MOE_DATA_PARQUET does not exist: {root}")
    parquet_dir = _parquet_dir(root)
    symbol_dir = parquet_dir / f"symbol={symbol}"
    if not symbol_dir.is_dir():
        raise SystemExit(
            f"No Hive partition {symbol_dir} for MOE_SYMBOL={symbol!r}. "
            "MOE_DATA_PARQUET should be the dataset root that contains "
            "parquet/symbol=SYMBOL/security=HASH/year=YYYY/data.parquet."
        )
    securities = _list_partition(symbol_dir, "security")
    chosen = _choose_security(symbol, securities, security)
    part_root = symbol_dir / f"security={chosen}"
    years = _list_partition(part_root, "year")
    minutes = _read_minute_files(part_root)
    daily = aggregate_regular_minutes(minutes)
    return daily, chosen, years


def aggregate_regular_minutes(minutes: pd.DataFrame) -> pd.DataFrame:
    """Filter regular-session traded minutes and aggregate them to daily OHLCV.

    Open is the first `FirstTradePrice` of the day, High/Low are the max/min
    trade prices, Close/Last is the last `LastTradePrice`, and Volume is the sum.
    Blank or empty trade prices are minutes with no trades and are dropped.
    """
    time_col = next((col for col in TIME_COLUMNS if col in minutes.columns), None)
    required = ["Date", "AuditSession", *PRICE_COLUMNS, "Volume"]
    missing = [col for col in required if col not in minutes.columns]
    if time_col is None:
        missing.append("TimeBarStart")
    if missing:
        found = sorted(minutes.columns.astype(str))
        raise SystemExit(
            f"Minute bars are missing columns {missing}. Found {found}."
        )

    session = minutes["AuditSession"].map(_as_text)
    work = minutes.loc[session == REGULAR_SESSION].copy()
    if work.empty:
        raise SystemExit(
            "No minute bars with AuditSession == 'regular' after filtering."
        )

    for col in PRICE_COLUMNS:
        work[col] = _to_float(work[col])
    traded = work.loc[:, list(PRICE_COLUMNS)].notna().all(axis=1)
    work = work.loc[traded].copy()
    if work.empty:
        raise SystemExit(
            "Regular-session bars had no trade prices to aggregate. "
            "Blank FirstTradePrice / HighTradePrice / LowTradePrice / "
            "LastTradePrice minutes are skipped."
        )

    work["Volume"] = _to_float(work["Volume"]).fillna(0.0)
    work["_day"] = _parse_yyyymmdd(work["Date"])
    if work["_day"].isna().any():
        raise SystemExit(
            "Could not parse Date as YYYYMMDD on regular-session minute bars."
        )
    work["_ord"] = _parse_clock(work[time_col])
    if work["_ord"].isna().any():
        raise SystemExit(
            f"Could not parse {time_col} on regular-session minute bars. "
            "Expected a clock time such as HH:MM."
        )

    work = work.sort_values(["_day", "_ord"], kind="mergesort")
    grouped = work.groupby("_day", sort=True)
    daily = pd.DataFrame(
        {
            "Open": grouped["FirstTradePrice"].first(),
            "High": grouped["HighTradePrice"].max(),
            "Low": grouped["LowTradePrice"].min(),
            "Close/Last": grouped["LastTradePrice"].last(),
            "Volume": grouped["Volume"].sum(),
        }
    )
    daily.index.name = "Date"
    daily = daily.reset_index()
    return daily.loc[:, DAILY_COLUMNS].reset_index(drop=True)


def _read_minute_files(part_root: Path) -> pd.DataFrame:
    files = sorted(path for path in part_root.rglob("*.parquet") if path.is_file())
    if not files:
        raise SystemExit(f"No parquet files under {part_root}.")
    try:
        import pyarrow.dataset as ds
    except ImportError as exc:
        raise SystemExit(
            "Reading MOE_DATA_PARQUET requires pyarrow. "
            "Install the pinned pyarrow dependency."
        ) from exc
    try:
        # Pass only the part files. symbol= and security= were already chosen
        # from the directory names, and a Hive _SUCCESS marker is not a table.
        dataset = ds.dataset([str(path) for path in files], format="parquet")
    except Exception as exc:
        raise SystemExit(f"Could not open Hive minute bars under {part_root} ({exc}).") from exc

    names = set(dataset.schema.names)
    time_col = next((col for col in TIME_COLUMNS if col in names), None)
    required = ["Date", "AuditSession", *PRICE_COLUMNS, "Volume"]
    missing = [col for col in required if col not in names]
    if time_col is None:
        missing.append("TimeBarStart")
    if missing:
        raise SystemExit(
            f"Minute bars at {part_root} are missing columns {missing}. "
            f"Found {sorted(names)}."
        )
    columns = ["Date", time_col, "AuditSession", *PRICE_COLUMNS, "Volume"]
    try:
        table = dataset.to_table(columns=columns)
    except Exception as exc:
        raise SystemExit(f"Could not read minute bars under {part_root} ({exc}).") from exc
    return table.to_pandas()


def _parquet_dir(root: Path) -> Path:
    nested = root / "parquet"
    if nested.is_dir():
        return nested
    try:
        has_symbol = any(
            child.is_dir() and child.name.startswith("symbol=")
            for child in root.iterdir()
        )
    except OSError as exc:
        raise SystemExit(f"Could not list MOE_DATA_PARQUET at {root} ({exc}).") from exc
    if has_symbol:
        return root
    raise SystemExit(
        f"No parquet/ directory or symbol=* partitions under {root}. "
        "Set MOE_DATA_PARQUET to the dataset root that contains "
        "parquet/symbol=SYMBOL/security=HASH/year=YYYY/data.parquet."
    )


def _list_partition(directory: Path, key: str) -> list[str]:
    prefix = f"{key}="
    found: list[str] = []
    try:
        children = list(directory.iterdir())
    except OSError as exc:
        raise SystemExit(f"Could not list {directory} ({exc}).") from exc
    for child in children:
        if child.is_dir() and child.name.startswith(prefix):
            found.append(child.name[len(prefix):])
    return sorted(found)


def _choose_security(symbol: str, securities: list[str], requested: str | None) -> str:
    if not securities:
        raise SystemExit(
            f"No security=* partition under symbol={symbol}. "
            "Expected parquet/symbol=SYMBOL/security=HASH/year=YYYY/data.parquet."
        )
    if requested is None:
        if len(securities) == 1:
            return securities[0]
        raise SystemExit(
            f"Symbol {symbol} has multiple securities {securities}. "
            "Set MOE_SECURITY to one of them."
        )
    if requested not in securities:
        raise SystemExit(
            f"MOE_SECURITY={requested!r} was not found under symbol={symbol}. "
            f"Found {securities}."
        )
    return requested


def _check_token(label: str, value: str) -> None:
    if (
        not value
        or "/" in value
        or "\\" in value
        or value in {".", ".."}
        or value.startswith(".")
    ):
        raise SystemExit(
            f"{label} must be a single Hive partition value, got {value!r}."
        )


def _missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return False
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _as_text(value: object) -> str:
    if _missing(value):
        return ""
    return str(value).strip()


def _float_cell(value: object) -> float:
    if isinstance(value, Decimal):
        return float(value)
    if _missing(value):
        return np.nan
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return np.nan
        try:
            return float(text)
        except ValueError:
            return np.nan
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return np.nan


def _to_float(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_object_dtype(series):
        return pd.to_numeric(series, errors="coerce").astype("float64")
    converted = series.map(_float_cell)
    return converted.astype("float64")


def _parse_yyyymmdd(series: pd.Series) -> pd.Series:
    def one(value: object) -> str | None:
        if isinstance(value, Decimal):
            value = int(value)
        if _missing(value):
            return None
        if isinstance(value, (int, np.integer)):
            text = f"{int(value):08d}"
        elif isinstance(value, float):
            if not value.is_integer():
                return None
            text = f"{int(value):08d}"
        else:
            text = str(value).strip()
            if text.endswith(".0"):
                text = text[:-2]
        if len(text) != 8 or not text.isdigit():
            return None
        return text

    return pd.to_datetime(series.map(one), format="%Y%m%d", errors="coerce")


def _parse_clock(series: pd.Series) -> pd.Series:
    def one(value: object) -> pd.Timedelta:
        if _missing(value):
            return pd.NaT
        match = _CLOCK.search(str(value).strip())
        if not match:
            return pd.NaT
        hour, minute, second, frac = match.groups()
        micro = int((frac + "000000")[:6]) if frac else 0
        try:
            return pd.Timedelta(
                hours=int(hour),
                minutes=int(minute),
                seconds=int(second or 0),
                microseconds=micro,
            )
        except ValueError:
            return pd.NaT

    return series.map(one)
