from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from src.models.base_model import BaseModel


class QuantLinearModel(BaseModel):
    """Wrapper for Logistic Regression / Ridge linear baseline models."""

    def __init__(self, mode: str = "regression", C: float = 1.0, max_iter: int = 1000):
        self.mode = mode.lower()
        if self.mode == "regression":
            self.model = Ridge(alpha=1.0 / C if C > 0 else 1.0)
        else:
            self.model = LogisticRegression(C=C, max_iter=max_iter, random_state=42)
        self.feature_names: list[str] = []

    def fit(self, X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray) -> QuantLinearModel:
        if isinstance(X, pd.DataFrame):
            self.feature_names = list(X.columns)
        self.model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        if self.mode == "classification" and hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        preds = self.predict(X)
        return np.column_stack([1.0 - preds, preds])


def build_model(mode: str = "regression", **kwargs):
    return QuantLinearModel(mode=mode, **kwargs)
