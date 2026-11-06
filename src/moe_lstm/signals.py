"""Study positions and the weights the engine can size.

Prediction 1 is long. Prediction 0 is flat. Class 0 is "not above the
threshold", so it is not a short. The in-process backtest and the engine
target weight use that same long-or-flat map.
"""

import numpy as np


def study_positions(predictions) -> np.ndarray:
    """Map 1 to long (+1) and 0 to flat (0)."""
    predicted = np.asarray(predictions)
    if predicted.size == 0:
        raise ValueError("Predictions are empty.")
    if not np.isin(predicted, (0, 1)).all():
        raise ValueError("Predictions must be 0 or 1.")
    return np.where(predicted == 1, 1.0, 0.0)


def long_only_target_weights(predictions) -> list[str]:
    """Decimal weight strings for one symbol. Long is ``1``. Flat is ``0``."""
    positions = study_positions(predictions)
    return ["1" if position > 0 else "0" for position in positions]
