"""
Voting Ensemble implementation (Hard & Soft Voting).
"""

from typing import List, Any
import numpy as np


class VotingEnsemble:
    """Combines model predictions via Hard or Soft Voting."""

    def __init__(self, mode: str = "soft"):
        self.mode = mode

    def predict(self, predictions_list: List[np.ndarray]) -> np.ndarray:
        if not predictions_list:
            return np.array([])

        preds_matrix = np.column_stack(predictions_list)
        if self.mode == "hard":
            # Majority vote on binary signs
            signs = np.sign(preds_matrix)
            return np.sign(np.sum(signs, axis=1))
        else:
            # Soft voting: average continuous predictions
            return np.mean(preds_matrix, axis=1)
