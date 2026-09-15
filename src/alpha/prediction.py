from __future__ import annotations
import numpy as np
import pandas as pd


def normalize_alpha(predictions: np.ndarray | pd.Series | float, scale: float = 0.05) -> np.ndarray | float:
    """Normalize raw model expected return predictions into a bounded alpha score in [-1.0, +1.0].

    Uses hyperbolic tangent scaling. An expected return of +5% maps to ~+0.76 alpha.
    """
    preds = np.asarray(predictions, dtype=float)
    alpha = np.tanh(preds / scale)
    if isinstance(predictions, (float, int)):
        return float(alpha)
    return alpha
