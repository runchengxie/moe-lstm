"""Mixture-of-experts LSTM for the next session's direction.

The package reads daily OHLC bars, builds technical features, selects subsets
with K-Means and a self-organizing map, and trains one LSTM mixture on each
subset. A prediction of 1 is long and 0 is flat: class 0 did not clear the
threshold, so it is not a short. The in-process backtest earns the next
close-to-close return only while long. Feature selection seeds are fixed. LSTM training
is not bitwise reproducible.

``MOE_DATA_PARQUET`` loads Hive minute bars and aggregates one row per session.
When that variable is unset, ``MOE_DATA_CSV`` (or the default URL) is the source.

Importing this package does not train a model and does not import TensorFlow.
"""

from __future__ import annotations

import importlib

_EXPORTS: dict[str, tuple[str, str]] = {
    "ANNUALIZATION_DAYS": ("moe_lstm.constants", "ANNUALIZATION_DAYS"),
    "BACKTEST_FEE": ("moe_lstm.constants", "BACKTEST_FEE"),
    "BATCH_SIZE": ("moe_lstm.constants", "BATCH_SIZE"),
    "DEFAULT_DATA_URL": ("moe_lstm.constants", "DEFAULT_DATA_URL"),
    "EPOCHS": ("moe_lstm.constants", "EPOCHS"),
    "KMEANS_N_INIT": ("moe_lstm.constants", "KMEANS_N_INIT"),
    "KMEANS_RANDOM_STATE": ("moe_lstm.constants", "KMEANS_RANDOM_STATE"),
    "LOOKBACK": ("moe_lstm.constants", "LOOKBACK"),
    "MANUAL_FEATURE_COLUMNS": ("moe_lstm.constants", "MANUAL_FEATURE_COLUMNS"),
    "METRIC_COLUMNS": ("moe_lstm.constants", "METRIC_COLUMNS"),
    "N_CLUSTERS": ("moe_lstm.constants", "N_CLUSTERS"),
    "PATIENCE": ("moe_lstm.constants", "PATIENCE"),
    "PREDICTION_THRESHOLD": ("moe_lstm.constants", "PREDICTION_THRESHOLD"),
    "PRICE_COLUMNS": ("moe_lstm.constants", "PRICE_COLUMNS"),
    "REQUIRED_COLUMNS": ("moe_lstm.constants", "REQUIRED_COLUMNS"),
    "SOM_COLS": ("moe_lstm.constants", "SOM_COLS"),
    "SOM_ITERATIONS": ("moe_lstm.constants", "SOM_ITERATIONS"),
    "SOM_LEARNING_RATE": ("moe_lstm.constants", "SOM_LEARNING_RATE"),
    "SOM_ROWS": ("moe_lstm.constants", "SOM_ROWS"),
    "SOM_SEED": ("moe_lstm.constants", "SOM_SEED"),
    "SOM_SIGMA": ("moe_lstm.constants", "SOM_SIGMA"),
    "THRESHOLD": ("moe_lstm.constants", "THRESHOLD"),
    "TRAIN_FRACTION": ("moe_lstm.constants", "TRAIN_FRACTION"),
    "VAL_FRACTION": ("moe_lstm.constants", "VAL_FRACTION"),
    "WARMUP_COLUMNS": ("moe_lstm.constants", "WARMUP_COLUMNS"),
    "WindowSplit": ("moe_lstm.constants", "WindowSplit"),
    "build_feature_frame": ("moe_lstm.data", "build_feature_frame"),
    "cluster_matrix": ("moe_lstm.data", "cluster_matrix"),
    "label_directions": ("moe_lstm.data", "label_directions"),
    "load_price_csv": ("moe_lstm.data", "load_price_csv"),
    "load_study_prices": ("moe_lstm.data", "load_study_prices"),
    "make_windows": ("moe_lstm.data", "make_windows"),
    "prediction_rows": ("moe_lstm.data", "prediction_rows"),
    "relative_strength_index": ("moe_lstm.data", "relative_strength_index"),
    "resolve_data_path": ("moe_lstm.data", "resolve_data_path"),
    "scale_features": ("moe_lstm.data", "scale_features"),
    "select_kmeans_features": ("moe_lstm.data", "select_kmeans_features"),
    "select_som_features": ("moe_lstm.data", "select_som_features"),
    "session_gap_warning": ("moe_lstm.data", "session_gap_warning"),
    "window_split": ("moe_lstm.data", "window_split"),
    "load_price_frame": ("moe_lstm.prices", "load_price_frame"),
    "build_moe_model": ("moe_lstm.model", "build_moe_model"),
    "resolve_epochs": ("moe_lstm.train", "resolve_epochs"),
    "train_and_predict_moe": ("moe_lstm.train", "train_and_predict_moe"),
    "backtest": ("moe_lstm.eval", "backtest"),
    "buy_and_hold_equity": ("moe_lstm.eval", "buy_and_hold_equity"),
    "classification_scores": ("moe_lstm.eval", "classification_scores"),
    "long_only_target_weights": ("moe_lstm.signals", "long_only_target_weights"),
    "study_positions": ("moe_lstm.signals", "study_positions"),
    "main": ("moe_lstm.cli", "main"),
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr = target
    module = importlib.import_module(module_name)
    value = getattr(module, attr)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_EXPORTS))
