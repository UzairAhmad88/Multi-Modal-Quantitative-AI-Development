from __future__ import annotations
import joblib
from pathlib import Path
from typing import Any, Dict
import numpy as np
import pandas as pd
try:
    from xgboost import XGBRegressor, XGBClassifier
except Exception:
    from sklearn.ensemble import HistGradientBoostingRegressor as XGBRegressor, HistGradientBoostingClassifier as XGBClassifier
from src.models.base_model import BaseModel
from src.utils.logger import get_logger

logger = get_logger("xgboost_model")


class QuantXGBoostModel(BaseModel):
    """Wrapper for XGBoost tabular alpha engine model supporting regression and classification."""

    def __init__(self, mode: str = "regression", hyperparams: Dict[str, Any] | None = None):
        self.mode = mode.lower()
        default_params = {
            "n_estimators": 300,
            "max_depth": 4,
            "learning_rate": 0.03,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "n_jobs": -1
        }
        if hyperparams:
            default_params.update(hyperparams)

        if self.mode == "regression":
            try:
                self.model = XGBRegressor(**default_params)
            except Exception:
                from sklearn.ensemble import HistGradientBoostingRegressor
                self.model = HistGradientBoostingRegressor(random_state=42)
        else:
            default_params.setdefault("eval_metric", "logloss")
            try:
                self.model = XGBClassifier(**default_params)
            except Exception:
                from sklearn.ensemble import HistGradientBoostingClassifier
                self.model = HistGradientBoostingClassifier(random_state=42)

        self.feature_names: list[str] = []

    def fit(self, X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray) -> QuantXGBoostModel:
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

    def get_feature_importance(self) -> pd.Series:
        return self.feature_importances

    @property
    def feature_importances(self) -> pd.Series:
        if hasattr(self.model, "feature_importances_"):
            imp = self.model.feature_importances_
            names = self.feature_names or [f"f_{i}" for i in range(len(imp))]
            return pd.Series(imp, index=names).sort_values(ascending=False)
        return pd.Series(dtype=float)

    def save_model(self, file_path: Path | str) -> None:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "mode": self.mode, "feature_names": self.feature_names}, file_path)
        logger.info(f"Saved XGBoost model to {file_path}")

    @classmethod
    def load_model(cls, file_path: Path | str) -> QuantXGBoostModel:
        data = joblib.load(file_path)
        instance = cls(mode=data["mode"])
        instance.model = data["model"]
        instance.feature_names = data["feature_names"]
        logger.info(f"Loaded XGBoost model from {file_path}")
        return instance


def build_model(mode: str = "regression", **kwargs):
    return QuantXGBoostModel(mode=mode, hyperparams=kwargs)
