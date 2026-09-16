"""
Averaging Ensemble implementation (Simple & Weighted Averaging).
"""

from typing import List, Optional
import numpy as np


class AveragingEnsemble:
    """Combines model predictions using Simple or Explicitly Weighted Averaging."""

    def predict(self, predictions_list: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray:
        if not predictions_list:
            return np.array([])

        preds_matrix = np.column_stack(predictions_list)
        if weights is None:
            return np.mean(preds_matrix, axis=1)

        w = np.array(weights) / np.sum(weights)
        return np.dot(preds_matrix, w)
