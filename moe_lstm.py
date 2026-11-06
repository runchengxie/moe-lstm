"""Mixture-of-experts LSTM for the next session's index direction.

The script reads daily OHLC bars, builds technical features, selects subsets
with K-Means and a self-organizing map, and trains one LSTM mixture on each
subset. A prediction of 1 is long and 0 is flat. Class 0 did not clear the
threshold, so the backtest does not short it. The backtest earns the next
close-to-close return while long. Feature selection seeds are fixed. LSTM training is not
bitwise reproducible.

`MOE_DATA_PARQUET` loads Hive minute bars and aggregates one row per session.
When that variable is unset, `MOE_DATA_CSV` (or the default URL) is the source.

中文说明与上面相同。脚本读取日频 OHLC，计算技术指标，用 K-Means 和自组织映射挑选
特征子集，并分别训练 LSTM 混合专家。预测 1 做多，0 空仓。类别 0 含小涨，
回测不做空。持有多头时赚取下一根 K 线的收盘到收盘收益。特征选择的随机种子是固定的，LSTM 训练结果不能逐位复现。
设置 `MOE_DATA_PARQUET` 时读取 Hive 分钟线并聚合成日线；未设置时使用
`MOE_DATA_CSV` 或默认 URL。
类别计数只打印，不重采样。三个专家读同一段输入，差别来自初始化和门控权重。
"""

import os
from collections import defaultdict
from collections.abc import Mapping
from typing import NamedTuple

import numpy as np
import pandas as pd
from minisom import MiniSom
from sklearn.cluster import KMeans
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import MinMaxScaler

from price_data import load_price_frame

# Study defaults. The dependency pins do not select a K-Means solver, so
# K-Means sets n_init explicitly: sklearn 1.4 changed the default from 10 to "auto".
LOOKBACK = 5
THRESHOLD = 0.002
N_CLUSTERS = 5
TRAIN_FRACTION = 0.8
VAL_FRACTION = 0.2
BACKTEST_FEE = 0.0005
EPOCHS = 50
BATCH_SIZE = 16
PATIENCE = 5
ANNUALIZATION_DAYS = 252
PREDICTION_THRESHOLD = 0.5
KMEANS_RANDOM_STATE = 42
KMEANS_N_INIT = 10
SOM_ROWS = 3
SOM_COLS = 3
SOM_SIGMA = 0.5
SOM_LEARNING_RATE = 0.5
SOM_ITERATIONS = 100
SOM_SEED = 42

DEFAULT_DATA_URL = (
    "https://raw.githubusercontent.com/runchengxie/quant_practice_3/"
    "refs/heads/main/historical_data.csv"
)
REQUIRED_COLUMNS = ("Date", "Close/Last", "Open", "High", "Low")
PRICE_COLUMNS = ("Close/Last", "Open", "High", "Low")
MANUAL_FEATURE_COLUMNS = (
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
)
WARMUP_COLUMNS = (
    "MA5",
    "MA10",
    "EMA5",
    "EMA10",
    "RSI",
    "MA20",
    "STD20",
    "BB_upper",
    "BB_lower",
    "MACD",
    "Signal_line",
    "Daily_Return",
    "Volatility",
)
METRIC_COLUMNS = (
    "Model",
    "Accuracy",
    "Precision",
    "Recall",
    "F1",
    "AUC-ROC",
    "Total Return",
    "Max Drawdown",
    "Sharpe Ratio",
)


class WindowSplit(NamedTuple):
    n_fit: int
    n_val: int
    n_test: int
    n_scale_rows: int


def resolve_data_path() -> str:
    return os.environ.get("MOE_DATA_CSV", DEFAULT_DATA_URL)


def resolve_epochs(epochs: int | None = None) -> int:
    """Epoch count for one training run.

    An explicit argument wins. Otherwise ``MOE_EPOCHS`` overrides the study
    default of 50. The variable is read when training starts, not at import.
    """
    if epochs is not None:
        if epochs < 1:
            raise ValueError(f"epochs must be a positive integer. Got {epochs}.")
        return epochs
    raw = os.environ.get("MOE_EPOCHS")
    if raw is None or raw.strip() == "":
        return EPOCHS
    try:
        value = int(raw)
    except ValueError as exc:
        raise SystemExit(f"MOE_EPOCHS must be a positive integer. Got {raw!r}.") from exc
    if value < 1:
        raise SystemExit(f"MOE_EPOCHS must be a positive integer. Got {raw!r}.")
    return value


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


def classification_scores(y_true, y_score, y_pred) -> dict[str, float]:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    scores = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    if np.unique(y_true).size < 2:
        scores["auc_roc"] = float("nan")
    else:
        scores["auc_roc"] = float(roc_auc_score(y_true, y_score))
    return scores


def study_positions(predictions) -> np.ndarray:
    """Map 1 to long (+1) and 0 to flat (0)."""
    predicted = np.asarray(predictions)
    if predicted.size == 0:
        raise ValueError("Predictions are empty.")
    if not np.isin(predicted, (0, 1)).all():
        raise ValueError("Predictions must be 0 or 1.")
    return np.where(predicted == 1, 1.0, 0.0)


def oos_probability_frame(dates, model_name: str, probabilities, predictions) -> pd.DataFrame:
    """Out-of-sample dates, probabilities, and hard labels for one model."""
    probability = np.asarray(probabilities, dtype=float).reshape(-1)
    predicted = np.asarray(predictions).reshape(-1)
    date = pd.Series(dates).reset_index(drop=True)
    if not (len(date) == len(probability) == len(predicted)):
        raise ValueError(
            "OOS dates, probabilities, and predictions must have the same length. "
            f"Got {len(date)}, {len(probability)}, {len(predicted)}."
        )
    if len(date) == 0:
        raise ValueError("OOS frame is empty.")
    if not np.isfinite(probability).all():
        raise ValueError("OOS probabilities must be finite.")
    return pd.DataFrame(
        {
            "Date": date,
            "Model": model_name,
            "Probability": probability,
            "Prediction": predicted.astype(int),
        }
    )


def write_oos_probabilities(frames: list[pd.DataFrame], path: str) -> str:
    """Write one CSV of out-of-sample probabilities. Returns ``path``."""
    if not frames:
        raise ValueError("No OOS frames to write.")
    table = pd.concat(frames, ignore_index=True)
    table.to_csv(path, index=False)
    return path


def backtest(predictions, df_test: pd.DataFrame, model_name: str, fee: float = BACKTEST_FEE) -> dict:
    """Long-or-flat backtest on the forward close-to-close return.

    ``Tomorrow_Change`` is the return from this close to the next close, which
    is the return the label used. ``Daily_Return`` on the same row already
    happened by that close, so it is not the strategy return.

    Prediction 1 is long (+1). Prediction 0 is flat (0). The account starts at
    1 before the first test bar. Opening or closing a long costs ``fee`` once.
    Staying flat earns nothing and pays nothing.

    Max drawdown uses a running peak of at least 1, so a loss from the starting
    equity counts even when later equity is lower still.
    """
    predicted = np.asarray(predictions)
    if len(predicted) != len(df_test):
        raise ValueError(
            f"Prediction length {len(predicted)} does not match {len(df_test)} backtest rows."
        )
    if len(predicted) == 0:
        raise ValueError("Backtest received no predictions.")
    if not np.isin(predicted, (0, 1)).all():
        raise ValueError("Predictions must be 0 or 1.")
    if "Tomorrow_Change" not in df_test.columns:
        raise ValueError("Backtest requires Tomorrow_Change.")
    forward = df_test["Tomorrow_Change"].to_numpy(dtype=float)
    if not np.isfinite(forward).all():
        raise ValueError("Tomorrow_Change must be finite on every backtest row.")

    position = study_positions(predicted)
    previous = np.empty_like(position)
    previous[0] = 0.0
    if len(position) > 1:
        previous[1:] = position[:-1]
    turnover = np.abs(position - previous)
    strategy = position * forward - fee * turnover

    strategy_series = pd.Series(strategy, index=df_test.index)
    equity = (1 + strategy_series).cumprod()
    equity.name = f"{model_name}_Cumulative"
    running_peak = equity.cummax().clip(lower=1.0)
    drawdown = (equity - running_peak) / running_peak
    deviation = float(strategy_series.std(ddof=1))
    if deviation == 0.0 or not np.isfinite(deviation):
        sharpe_ratio = float("nan")
    else:
        sharpe_ratio = float(strategy_series.mean() / deviation * np.sqrt(ANNUALIZATION_DAYS))

    return {
        "Model": model_name,
        "Total Return": float(equity.iloc[-1] - 1),
        "Max Drawdown": float(drawdown.min()),
        "Sharpe Ratio": sharpe_ratio,
        "Cumulative": equity,
    }


def build_moe_model(lookback: int, n_features: int):
    import tensorflow.keras.backend as K
    from tensorflow.keras.layers import LSTM, Dense, Flatten, Input, Lambda
    from tensorflow.keras.models import Model

    inputs = Input(shape=(lookback, n_features), name="Input_Sequence")
    experts = []
    for index in range(1, 4):
        sequence = LSTM(64, return_sequences=True, name=f"LSTM_Expert_{index}")(inputs)
        experts.append(Flatten(name=f"Flatten_Expert_{index}")(sequence))
    gate = Dense(3, activation="softmax", name="Gating_Network")(inputs[:, -1, :])
    # Stack experts on a new axis so the 3 gate weights can scale them.
    # Concatenating on the feature axis cannot broadcast against that gate.
    stacked = Lambda(lambda tensors: K.stack(tensors, axis=1), name="Stack_Experts")(experts)
    weighted = Lambda(
        lambda pair: K.sum(pair[0] * K.expand_dims(pair[1], axis=-1), axis=1),
        name="Weighted_Sum",
    )([stacked, gate])
    output = Dense(1, activation="sigmoid", name="Final_Output")(weighted)
    model = Model(inputs=inputs, outputs=output, name="MOE_LSTM_Model")
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def train_and_predict_moe(
    frame: pd.DataFrame,
    feature_list,
    model_name: str,
    lookback: int = LOOKBACK,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    patience: int = PATIENCE,
) -> dict:
    """Fit one mixture on ``feature_list`` and score the untouched test windows."""
    missing = [name for name in feature_list if name not in frame.columns]
    if missing:
        raise ValueError(f"Missing features {missing}.")
    values = frame.loc[:, list(feature_list)].to_numpy(dtype=float)
    labels = frame["Target"].to_numpy()
    split = window_split(len(frame), lookback)
    scaled = scale_features(values, split.n_scale_rows)
    windows, targets = make_windows(scaled, labels, lookback)
    n_train = split.n_fit + split.n_val
    x_fit, y_fit = windows[: split.n_fit], targets[: split.n_fit]
    x_val, y_val = windows[split.n_fit : n_train], targets[split.n_fit : n_train]
    x_test, y_test = windows[n_train:], targets[n_train:]

    from tensorflow.keras.callbacks import EarlyStopping

    model = build_moe_model(lookback, len(feature_list))
    model.fit(
        x_fit,
        y_fit.astype("float32"),
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(x_val, y_val.astype("float32")),
        callbacks=[EarlyStopping(patience=patience, restore_best_weights=True)],
        verbose=0,
    )
    y_score = model.predict(x_test, verbose=0).flatten()
    y_pred = (y_score > PREDICTION_THRESHOLD).astype(int)
    scores = classification_scores(y_test, y_score, y_pred)
    print(f"\n===== {model_name} 分类报告 =====")
    print(classification_report(y_test, y_pred, zero_division=0))
    return {
        "model_name": model_name,
        "y_test": y_test,
        "predictions": y_pred,
        "accuracy": scores["accuracy"],
        "precision": scores["precision"],
        "recall": scores["recall"],
        "f1": scores["f1"],
        "auc_roc": scores["auc_roc"],
        "probabilities": y_score,
        "model": model,
    }


def buy_and_hold_equity(forward_returns: pd.Series) -> pd.Series:
    """Uncosted equity of holding through the same forward returns as the strategy."""
    return (1 + forward_returns).cumprod()


def _show(plt) -> None:
    """Display figures on an interactive backend and stay quiet under Agg."""
    import matplotlib

    if matplotlib.get_backend().lower() == "agg":
        plt.close("all")
        return
    plt.show()


def _print_overview(frame: pd.DataFrame) -> None:
    print("===== 数据前几行 =====")
    print(frame.head())
    print("\n===== 数据信息 =====")
    print(frame.info())
    print("\n===== 描述统计 =====")
    print(frame.describe())
    print("\n===== 缺失值统计 =====")
    print(frame.isnull().sum())


def _plot_close(frame: pd.DataFrame) -> None:
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    plt.plot(frame["Date"], frame["Close/Last"], label="Close Price")
    axis = plt.gca()
    axis.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.title("Close Price over Time")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.setp(axis.xaxis.get_majorticklabels(), rotation=45)
    _show(plt)


def _plot_correlation(frame: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Descriptive only. Feature selection uses the fit rows, not this matrix.
    correlation = frame[list(MANUAL_FEATURE_COLUMNS)].corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation, annot=True, cmap="coolwarm")
    plt.title("Correlation Matrix of Selected Features")
    _show(plt)


def _plot_results(results: list[dict], df_test: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.figure(figsize=(15, 4))
    for index, result in enumerate(results):
        plt.subplot(1, len(results), index + 1)
        matrix = confusion_matrix(result["y_test"], result["predictions"], labels=[0, 1])
        sns.heatmap(
            matrix,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=["Not above", "Above"],
            yticklabels=["Not above", "Above"],
        )
        plt.title(f"{result['Model']} Confusion Matrix")
        plt.xlabel("Predicted")
        plt.ylabel("True")
    plt.tight_layout()
    _show(plt)

    plt.figure(figsize=(14, 7))
    for result in results:
        plt.plot(df_test["Date"], result["Cumulative"], label=result["Model"])
    plt.plot(
        df_test["Date"],
        buy_and_hold_equity(df_test["Tomorrow_Change"]),
        label="Buy & Hold",
        linestyle="--",
    )
    plt.title("Cumulative Returns Comparison")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.legend()
    plt.xticks(rotation=45)
    _show(plt)

    # Percent change of each equity curve, including the first NaN point.
    plt.figure(figsize=(14, 5))
    for result in results:
        plt.plot(df_test["Date"], result["Cumulative"].pct_change(), label=result["Model"])
    plt.title("Daily Returns Comparison")
    plt.xlabel("Date")
    plt.ylabel("Daily Return")
    plt.legend()
    _show(plt)


def _metrics_table(results: list[dict]) -> pd.DataFrame:
    return pd.DataFrame([{column: result[column] for column in METRIC_COLUMNS} for result in results])


def main(epochs: int | None = None) -> pd.DataFrame:
    epochs = resolve_epochs(epochs)
    raw = load_study_prices()
    _print_overview(raw)
    _plot_close(raw)

    try:
        frame = build_feature_frame(raw, THRESHOLD)
        split = window_split(len(frame), LOOKBACK)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    warning = session_gap_warning(frame["Date"])
    if warning:
        print(warning)

    print(frame[["Date", "Close/Last", "Daily_Return", "Tomorrow_Change", "Target"]].head(10))
    balance_counts = frame["Target"].value_counts()
    print("标签分布：")
    print(balance_counts)
    print("\n占比：")
    print(balance_counts / len(frame))
    _plot_correlation(frame)

    manual = list(MANUAL_FEATURE_COLUMNS)
    clustered = cluster_matrix(frame.loc[:, manual].to_numpy(dtype=float), split.n_scale_rows)
    kmeans_columns = select_kmeans_features(clustered, manual, N_CLUSTERS)
    som_columns = select_som_features(clustered, manual)
    print("K-Means Selected Features:", kmeans_columns)
    print("SOM Selected Features:", som_columns)

    df_test = prediction_rows(frame, LOOKBACK, split.n_test)
    results = []
    for feature_columns, model_name in zip(
        (manual, kmeans_columns, som_columns),
        ("Manual", "KMeans", "SOM"),
    ):
        model_result = train_and_predict_moe(
            frame,
            feature_columns,
            model_name,
            LOOKBACK,
            epochs=epochs,
        )
        if len(model_result["predictions"]) != len(df_test):
            raise RuntimeError("Test prediction length does not match the backtest rows.")
        backtest_result = backtest(model_result["predictions"], df_test, model_name)
        results.append(
            {
                "Model": model_name,
                "y_test": model_result["y_test"],
                "predictions": model_result["predictions"],
                "probabilities": model_result["probabilities"],
                "Accuracy": model_result["accuracy"],
                "Precision": model_result["precision"],
                "Recall": model_result["recall"],
                "F1": model_result["f1"],
                "AUC-ROC": model_result["auc_roc"],
                "Total Return": backtest_result["Total Return"],
                "Max Drawdown": backtest_result["Max Drawdown"],
                "Sharpe Ratio": backtest_result["Sharpe Ratio"],
                "Cumulative": backtest_result["Cumulative"],
            }
        )

    oos_path = os.environ.get("MOE_OOS_CSV", "oos_probabilities.csv")
    write_oos_probabilities(
        [
            oos_probability_frame(
                df_test["Date"],
                result["Model"],
                result["probabilities"],
                result["predictions"],
            )
            for result in results
        ],
        oos_path,
    )
    print(f"OOS probabilities written to {oos_path}")

    metrics = _metrics_table(results)
    print("\n===== 模型性能对比 =====")
    print(metrics.round(3))
    _plot_results(results, df_test)
    print(metrics[["Model", "Total Return", "Max Drawdown", "Sharpe Ratio"]])
    return metrics


if __name__ == "__main__":
    main()
