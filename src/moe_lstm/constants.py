"""Study defaults shared by the data, training, and evaluation modules.

The dependency pins do not select a K-Means solver, so K-Means sets n_init
explicitly: sklearn 1.4 changed the default from 10 to "auto".
"""

from typing import NamedTuple

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
