"""Fit one mixture and score the untouched test windows."""

import os

import pandas as pd
from sklearn.metrics import classification_report

from moe_lstm.constants import BATCH_SIZE, EPOCHS, LOOKBACK, PATIENCE, PREDICTION_THRESHOLD
from moe_lstm.data import make_windows, scale_features, window_split
from moe_lstm.eval import classification_scores
from moe_lstm.model import build_moe_model

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
        "model": model,
    }

