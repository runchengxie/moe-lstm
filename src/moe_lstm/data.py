"""Daily bars, indicators, the chronological split, and feature selection."""

import os
from collections import defaultdict
from collections.abc import Mapping

import numpy as np
import pandas as pd
from minisom import MiniSom
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

from moe_lstm.constants import (
    ANNUALIZATION_DAYS,
    DEFAULT_DATA_URL,
    KMEANS_N_INIT,
    KMEANS_RANDOM_STATE,
    LOOKBACK,
    N_CLUSTERS,
    PRICE_COLUMNS,
    REQUIRED_COLUMNS,
    SOM_COLS,
    SOM_ITERATIONS,
    SOM_LEARNING_RATE,
    SOM_ROWS,
    SOM_SEED,
    SOM_SIGMA,
    THRESHOLD,
    TRAIN_FRACTION,
    VAL_FRACTION,
    WARMUP_COLUMNS,
    WindowSplit,
)
from moe_lstm.prices import load_price_frame

def resolve_data_path() -> str:
    return os.environ.get("MOE_DATA_CSV", DEFAULT_DATA_URL)


def load_price_csv(data_path: str) -> pd.DataFrame:
    """Read the CSV contract and reject values the indicators cannot use.

    Extra columns are kept for the preview print. They are not features.
    """
    try:
        frame = pd.read_csv(data_path)
    except Exception as exc:
        raise SystemExit(
            f"Could not read price data from {data_path!r} ({exc}). "
            "Set MOE_DATA_CSV to a local CSV with columns "
            "Date (%m/%d/%Y), Close/Last, Open, High, and Low. "
            "Price columns must be numeric."
        ) from exc

    missing = [name for name in REQUIRED_COLUMNS if name not in frame.columns]
    if missing:
        raise SystemExit(
            f"Price data from {data_path!r} is missing columns {missing}. "
            "Required columns: Date (%m/%d/%Y), Close/Last, Open, High, Low."
        )
    if frame.empty:
        raise SystemExit(f"Price data from {data_path!r} has no rows.")

    parsed = frame.copy()
    try:
        parsed["Date"] = pd.to_datetime(parsed["Date"], format="%m/%d/%Y")
    except (ValueError, TypeError) as exc:
        raise SystemExit(
            f"Could not parse Date in {data_path!r} with format %m/%d/%Y ({exc}). "
            "An accepted value is 01/13/2020. ISO dates are not accepted."
        ) from exc

    duplicate_count = int(parsed["Date"].duplicated().sum())
    if duplicate_count:
        raise SystemExit(
            f"Date has {duplicate_count} duplicate values in {data_path!r}. "
            "Each session needs one row."
        )

    for column in PRICE_COLUMNS:
        converted = pd.to_numeric(parsed[column], errors="coerce")
        values = converted.to_numpy(dtype=float)
        if converted.isna().any() or not np.isfinite(values).all():
            raise SystemExit(
                f"Column {column} in {data_path!r} must contain finite numbers. "
                "A currency symbol or thousands separator is not accepted."
            )
        parsed[column] = converted

    if (parsed["Close/Last"] <= 0).any():
        raise SystemExit(
            f"Close/Last in {data_path!r} must be positive so close-to-close "
            "returns are defined."
        )

    return parsed.sort_values("Date").reset_index(drop=True)


def load_study_prices(env: Mapping[str, str] | None = None) -> pd.DataFrame:
    """Daily bars for one study run.

    A non-empty ``MOE_DATA_PARQUET`` reads Hive minute bars and wins over
    ``MOE_DATA_CSV``. The CSV path still uses the strict column contract.
    """
    if env is None:
        env = os.environ
    if str(env.get("MOE_DATA_PARQUET", "")).strip():
        frame = load_price_frame(env)
        return frame.sort_values("Date").reset_index(drop=True)
    if "MOE_DATA_CSV" in env:
        path = env["MOE_DATA_CSV"]
    else:
        path = DEFAULT_DATA_URL
    return load_price_csv(path)


def relative_strength_index(close: pd.Series, window: int = 14) -> pd.Series:
    """Simple-average RSI. A flat window is 50, not NaN, so it is not deleted."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rsi = pd.Series(np.nan, index=close.index, dtype=float)
    both_zero = (avg_gain == 0) & (avg_loss == 0)
    no_loss = (avg_loss == 0) & (avg_gain > 0)
    no_gain = (avg_gain == 0) & (avg_loss > 0)
    normal = avg_loss > 0
    rsi.loc[normal] = 100 - (100 / (1 + (avg_gain[normal] / avg_loss[normal])))
    rsi.loc[no_loss] = 100.0
    rsi.loc[no_gain] = 0.0
    rsi.loc[both_zero] = 50.0
    return rsi


def label_directions(forward_returns: pd.Series, threshold: float = THRESHOLD) -> pd.Series:
    values = forward_returns.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Forward returns must be finite before labeling.")
    return pd.Series((values > threshold).astype(int), index=forward_returns.index)


def build_feature_frame(frame: pd.DataFrame, threshold: float = THRESHOLD) -> pd.DataFrame:
    """Add indicators and the next-session label.

    Rows are dropped only for indicator warmup and for the final session, whose
    next close is unknown. Empty extra columns do not remove sessions.
    """
    missing = [name for name in REQUIRED_COLUMNS if name not in frame.columns]
    if missing:
        raise ValueError(f"Feature frame is missing columns {missing}.")

    features = frame.sort_values("Date").reset_index(drop=True).copy()
    close = features["Close/Last"]
    features["MA5"] = close.rolling(window=5).mean()
    features["MA10"] = close.rolling(window=10).mean()
    features["EMA5"] = close.ewm(span=5, adjust=False).mean()
    features["EMA10"] = close.ewm(span=10, adjust=False).mean()
    features["RSI"] = relative_strength_index(close)
    features["MA20"] = close.rolling(window=20).mean()
    features["STD20"] = close.rolling(window=20).std()
    features["BB_upper"] = features["MA20"] + 2 * features["STD20"]
    features["BB_lower"] = features["MA20"] - 2 * features["STD20"]
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    features["MACD"] = ema12 - ema26
    features["Signal_line"] = features["MACD"].ewm(span=9, adjust=False).mean()
    features["Daily_Return"] = close.pct_change()
    features["Volatility"] = features["Daily_Return"].rolling(window=10).std()

    features = features.dropna(subset=list(WARMUP_COLUMNS)).reset_index(drop=True)
    # Daily_Return on row t+1 is the close-to-close move the label at t names.
    features["Tomorrow_Change"] = features["Daily_Return"].shift(-1)
    features = features.dropna(subset=["Tomorrow_Change"]).reset_index(drop=True)
    if features.empty:
        raise ValueError(
            "No rows left after dropping indicator warmup and the final session. "
            "A daily file needs at least 28 sessions."
        )
    features["Target"] = label_directions(features["Tomorrow_Change"], threshold)
    return features


def window_split(
    n_rows: int,
    lookback: int = LOOKBACK,
    train_fraction: float = TRAIN_FRACTION,
    val_fraction: float = VAL_FRACTION,
) -> WindowSplit:
    """Chronological fit, validation, and test window counts.

    Scaler rows are the feature rows of the fit windows. Validation is the tail
    of the training block. The test block is the last ``1 - train_fraction`` of
    the windows and is not included in ``n_scale_rows``.
    """
    if lookback < 1:
        raise ValueError("lookback must be positive.")
    n_windows = n_rows - lookback
    if n_windows < 1:
        raise ValueError(
            f"Need more than {lookback} rows to build one window. Got {n_rows}."
        )
    n_train = int(n_windows * train_fraction)
    n_test = n_windows - n_train
    if n_train < 2 or n_test < 1:
        raise ValueError(
            "Need at least two training windows and one test window. "
            f"Got rows={n_rows}, lookback={lookback}, train={n_train}, test={n_test}."
        )
    n_val = max(int(n_train * val_fraction), 1)
    n_fit = n_train - n_val
    if n_fit < 1:
        raise ValueError(
            "The validation holdout left no fit windows. "
            f"Got rows={n_rows}, lookback={lookback}, fit={n_fit}, val={n_val}."
        )
    # Last fit window starts at n_fit - 1 and covers `lookback` rows.
    n_scale_rows = n_fit + lookback - 1
    return WindowSplit(n_fit, n_val, n_test, n_scale_rows)


def scale_features(values: np.ndarray, n_scale_rows: int) -> np.ndarray:
    if n_scale_rows < 1 or n_scale_rows > len(values):
        raise ValueError(
            f"Scaler row count must be inside 1..{len(values)}. Got {n_scale_rows}."
        )
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(values[:n_scale_rows])
    return scaler.transform(values)


def cluster_matrix(values: np.ndarray, n_scale_rows: int) -> np.ndarray:
    """Scale on fit rows and return only that slice for feature selection."""
    return scale_features(values, n_scale_rows)[:n_scale_rows]


def select_kmeans_features(
    feature_matrix: np.ndarray,
    names: list[str] | tuple[str, ...],
    n_clusters: int = N_CLUSTERS,
) -> list[str]:
    if feature_matrix.ndim != 2 or feature_matrix.shape[1] != len(names):
        raise ValueError("K-Means input must have one column per feature name.")
    if feature_matrix.shape[1] < n_clusters:
        raise ValueError(
            f"K-Means needs at least {n_clusters} features. Got {feature_matrix.shape[1]}."
        )
    points = feature_matrix.T
    model = KMeans(
        n_clusters=n_clusters,
        random_state=KMEANS_RANDOM_STATE,
        n_init=KMEANS_N_INIT,
    )
    labels = model.fit_predict(points)
    selected = []
    for cluster_id in range(n_clusters):
        indices = np.flatnonzero(labels == cluster_id)
        if len(indices) == 0:
            continue
        distances = np.linalg.norm(points[indices] - model.cluster_centers_[cluster_id], axis=1)
        selected.append(names[int(indices[int(np.argmin(distances))])])
    if not selected:
        raise ValueError("K-Means selected no features.")
    return selected


def select_som_features(
    feature_matrix: np.ndarray,
    names: list[str] | tuple[str, ...],
) -> list[str]:
    if feature_matrix.ndim != 2 or feature_matrix.shape[1] != len(names):
        raise ValueError("SOM input must have one column per feature name.")
    points = feature_matrix.T
    som = MiniSom(
        SOM_ROWS,
        SOM_COLS,
        points.shape[1],
        sigma=SOM_SIGMA,
        learning_rate=SOM_LEARNING_RATE,
        random_seed=SOM_SEED,
    )
    som.train_random(points, SOM_ITERATIONS)
    grouped: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, point in enumerate(points):
        grouped[som.winner(point)].append(index)
    weights = som.get_weights()
    selected = []
    for (row, col), members in grouped.items():
        center = weights[row, col, :]
        distances = [np.linalg.norm(points[index] - center) for index in members]
        selected.append(names[members[int(np.argmin(distances))]])
    if not selected:
        raise ValueError("SOM selected no features.")
    return selected


def make_windows(
    scaled: np.ndarray, labels: np.ndarray, lookback: int
) -> tuple[np.ndarray, np.ndarray]:
    """Window ``i`` is feature rows ``i .. i+lookback-1``.

    Its label is row ``i+lookback``, the first row after the window. That row's
    forward return starts at its close and ends at the next close, so the
    window does not contain the close where the label becomes known.
    """
    n_windows = len(scaled) - lookback
    if n_windows < 1:
        raise ValueError("Not enough scaled rows to build a window.")
    windows = np.empty((n_windows, lookback, scaled.shape[1]), dtype=float)
    targets = np.empty(n_windows, dtype=int)
    for index in range(n_windows):
        windows[index] = scaled[index : index + lookback]
        targets[index] = labels[index + lookback]
    return windows, targets


def prediction_rows(frame: pd.DataFrame, lookback: int, n_test: int) -> pd.DataFrame:
    """Rows whose labels the test windows predict, in window order."""
    n_windows = len(frame) - lookback
    first_window = n_windows - n_test
    first_row = first_window + lookback
    rows = frame.iloc[first_row : first_row + n_test].copy()
    if len(rows) != n_test:
        raise ValueError(
            f"Expected {n_test} backtest rows, found {len(rows)} in a frame of {len(frame)}."
        )
    return rows


def session_gap_warning(dates: pd.Series) -> str | None:
    gaps = pd.Series(dates).sort_values().diff().dt.days.dropna()
    if gaps.empty:
        return None
    median_gap = float(gaps.median())
    if 1 <= median_gap <= 3:
        return None
    return (
        f"Warning: median date gap is {median_gap:g} days. "
        f"Sharpe uses sqrt({ANNUALIZATION_DAYS}), which assumes one bar per trading session."
    )

