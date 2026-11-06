"""Long-or-flat positions for a threshold label.

Prediction 1 is long. Prediction 0 is flat. Class 0 did not clear the threshold.
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

