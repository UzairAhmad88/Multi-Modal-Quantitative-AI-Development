"""
Blending Ensemble implementation.
Blends hold-out validation set predictions using convex linear combination.
"""

from typing import List, Optional
import numpy as np


class BlendingEnsemble:
    """Blends hold-out validation set predictions."""

    def predict(self, predictions_list: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray:
        if not predictions_list:
            return np.array([])
        preds_matrix = np.column_stack(predictions_list)
        if weights is None:
            return np.median(preds_matrix, axis=1)

        w = np.array(weights) / np.sum(weights)
        return np.dot(preds_matrix, w)
