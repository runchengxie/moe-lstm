"""Fit one mixture and score the untouched test windows."""

import os

import pandas as pd
from sklearn.metrics import classification_report

from moe_lstm.constants import (
    AUX_LOSS_WEIGHT,
    BATCH_SIZE,
    EPOCHS,
    LOOKBACK,
    N_EXPERTS,
    PATIENCE,
    PREDICTION_THRESHOLD,
    TOP_K,
)
from moe_lstm.data import make_windows, scale_features, window_split
from moe_lstm.eval import classification_scores
from moe_lstm.model import build_moe_model


class _Missing:
    """Sentinel so None can mean the dense gate rather than 'read the environment'."""


_MISSING = _Missing()


def _parse_top_k(value, error: type[Exception], label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if text.lower() in {"dense", "all", "none"}:
            return None
        try:
            value = int(text)
        except ValueError as exc:
            raise error(f"{label} must be a positive integer or 'dense'. Got {text!r}.") from exc
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise error(f"{label} must be a positive integer or 'dense'. Got {value!r}.")
    if value >= N_EXPERTS:
        raise error(
            f"{label} must be between 1 and {N_EXPERTS - 1}, or 'dense' for every expert. Got {value}."
        )
    return value


def resolve_top_k(top_k: int | None | _Missing = _MISSING) -> int | None:
    """Expert count kept by the gate.

    An explicit integer wins. ``None`` is the dense softmax. Omit the argument
    to read ``MOE_TOP_K`` (``dense``, ``all``, or ``none`` for the dense path).
    Unset, the study uses ``TOP_K``.
    """
    if not isinstance(top_k, _Missing):
        return _parse_top_k(top_k, ValueError, "top_k")
    raw = os.environ.get("MOE_TOP_K")
    if raw is None or raw.strip() == "":
        return TOP_K
    return _parse_top_k(raw, SystemExit, "MOE_TOP_K")


def _parse_aux_weight(value, error: type[Exception], label: str) -> float:
    if isinstance(value, str):
        text = value.strip()
        try:
            value = float(text)
        except ValueError as exc:
            raise error(f"{label} must be a nonnegative number. Got {text!r}.") from exc
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise error(f"{label} must be a nonnegative number. Got {value!r}.")
    weight = float(value)
    if weight < 0 or weight != weight or weight == float("inf"):
        raise error(f"{label} must be a nonnegative finite number. Got {value!r}.")
    return weight


def resolve_aux_loss_weight(
    weight: float | None | _Missing = _MISSING,
    top_k: int | None | _Missing = _MISSING,
) -> float:
    """Switch auxiliary coefficient. 0 leaves binary crossentropy alone.

    An explicit number wins. Omit it to read ``MOE_AUX_LOSS``. Unset, the
    sparse path uses ``AUX_LOSS_WEIGHT`` and the dense path uses 0.
    """
    resolved_top_k = resolve_top_k(top_k)
    if not isinstance(weight, _Missing):
        return _parse_aux_weight(weight, ValueError, "aux_loss_weight")
    raw = os.environ.get("MOE_AUX_LOSS")
    if raw is None or raw.strip() == "":
        return AUX_LOSS_WEIGHT if resolved_top_k is not None else 0.0
    return _parse_aux_weight(raw, SystemExit, "MOE_AUX_LOSS")


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
    top_k: int | None | _Missing = _MISSING,
    aux_loss_weight: float | None | _Missing = _MISSING,
) -> dict:
    """Fit one mixture on ``feature_list`` and score the untouched test windows.

    Omit ``top_k`` and ``aux_loss_weight`` to honor ``MOE_TOP_K`` and
    ``MOE_AUX_LOSS``. Pass ``top_k=None`` for the dense softmax.
    """
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

    model = build_moe_model(
        lookback,
        len(feature_list),
        top_k=resolve_top_k(top_k),
        aux_loss_weight=resolve_aux_loss_weight(aux_loss_weight, top_k),
    )
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

