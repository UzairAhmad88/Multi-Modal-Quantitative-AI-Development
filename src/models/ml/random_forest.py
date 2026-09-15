from __future__ import annotations
import joblib
from pathlib import Path
from typing import Any, Dict
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from src.models.base_model import BaseModel
from src.utils.logger import get_logger

logger = get_logger("random_forest")


class QuantRandomForestModel(BaseModel):
    """Wrapper for Random Forest tabular model supporting regression and classification."""

    def __init__(self, mode: str = "regression", hyperparams: Dict[str, Any] | None = None):
        self.mode = mode.lower()
        default_params = {
            "n_estimators": 200,
            "max_depth": 6,
            "random_state": 42,
            "n_jobs": -1
        }
        if hyperparams:
            default_params.update(hyperparams)

        if self.mode == "regression":
            self.model = RandomForestRegressor(**default_params)
        else:
            default_params.setdefault("class_weight", "balanced")
            self.model = RandomForestClassifier(**default_params)

        self.feature_names: list[str] = []

    def fit(self, X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray) -> QuantRandomForestModel:
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

    @property
    def feature_importances(self) -> pd.Series:
        if hasattr(self.model, "feature_importances_"):
            imp = self.model.feature_importances_
            names = self.feature_names or [f"f_{i}" for i in range(len(imp))]
            return pd.Series(imp, index=names).sort_values(ascending=False)
        return pd.Series(dtype=float)


def build_model(mode: str = "regression", **kwargs):
    return QuantRandomForestModel(mode=mode, hyperparams=kwargs)
