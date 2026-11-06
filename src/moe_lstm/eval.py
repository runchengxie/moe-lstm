"""Classification scores and the in-process long/short backtest.

This backtest is the study printout. It is not the quant-backtest-engine ledger.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from moe_lstm.constants import ANNUALIZATION_DAYS, BACKTEST_FEE

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


def backtest(predictions, df_test: pd.DataFrame, model_name: str, fee: float = BACKTEST_FEE) -> dict:
    """Long/short backtest on the forward close-to-close return.

    ``Tomorrow_Change`` is the return from this close to the next close, which
    is the return the label used. ``Daily_Return`` on the same row already
    happened by that close, so it is not the strategy return.

    The account is flat before the first test bar. Turnover is the absolute
    position change, so opening from flat costs ``fee`` and a long-to-short
    flip costs ``2 * fee``. An unchanged position costs nothing.
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

    position = np.where(predicted == 1, 1.0, -1.0)
    previous = np.empty_like(position)
    previous[0] = 0.0
    if len(position) > 1:
        previous[1:] = position[:-1]
    turnover = np.abs(position - previous)
    strategy = position * forward - fee * turnover

    strategy_series = pd.Series(strategy, index=df_test.index)
    equity = (1 + strategy_series).cumprod()
    equity.name = f"{model_name}_Cumulative"
    drawdown = (equity - equity.cummax()) / equity.cummax()
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


def buy_and_hold_equity(forward_returns: pd.Series) -> pd.Series:
    """Uncosted equity of holding through the same forward returns as the strategy."""
    return (1 + forward_returns).cumprod()

