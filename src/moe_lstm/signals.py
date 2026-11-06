"""Study positions and the long-only weights the engine can size.

`eval.backtest` still earns a long/short forward return. quant-backtest-engine
`size` accepts nonnegative target weights that sum to at most one, so a short
study signal is weight ``0`` (flat) on that path, not a short sale.
"""

import numpy as np


def study_positions(predictions) -> np.ndarray:
    """Map 1 to long (+1) and 0 to short (-1), the same rule as ``backtest``."""
    predicted = np.asarray(predictions)
    if predicted.size == 0:
        raise ValueError("Predictions are empty.")
    if not np.isin(predicted, (0, 1)).all():
        raise ValueError("Predictions must be 0 or 1.")
    return np.where(predicted == 1, 1.0, -1.0)


def long_only_target_weights(predictions) -> list[str]:
    """Decimal weight strings for one symbol. Long is ``1``. Short is ``0``."""
    positions = study_positions(predictions)
    return ["1" if position > 0 else "0" for position in positions]
