"""
Stacking Ensemble implementation.
Fits meta-learner on out-of-fold base model predictions.
"""

from typing import List, Any
import numpy as np
from sklearn.linear_model import Ridge


class StackingEnsemble:
    """Stacking classifier/regressor fitting Ridge meta-learner on base model predictions."""

    def __init__(self):
        self.meta_learner = Ridge(alpha=1.0)
        self.is_fitted = False

    def fit(self, base_predictions_list: List[np.ndarray], y_true: np.ndarray) -> Any:
        X_meta = np.column_stack(base_predictions_list)
        self.meta_learner.fit(X_meta, y_true)
        self.is_fitted = True
        return self

    def predict(self, base_predictions_list: List[np.ndarray]) -> np.ndarray:
        X_meta = np.column_stack(base_predictions_list)
        if not self.is_fitted:
            return np.mean(X_meta, axis=1)
        return self.meta_learner.predict(X_meta)
