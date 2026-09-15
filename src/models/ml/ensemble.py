from __future__ import annotations
from typing import Dict, List, Any
import numpy as np
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger("ensemble")


class EnsembleEngine:
    """Ensembles predictions from XGBoost, LSTM, GRU, Transformer, and Multi-Modal networks."""

    def __init__(self, method: str = "equal", weights: Dict[str, float] | None = None):
        self.method = method.lower()
        self.weights = weights or {}

    def fit_weights(self, val_predictions: Dict[str, np.ndarray], y_val: np.ndarray) -> Dict[str, float]:
        """Compute model ensemble weights strictly on validation set performance (never on test data)."""
        if self.method == "equal":
            n = len(val_predictions)
            self.weights = {name: 1.0 / n for name in val_predictions.keys()}
        elif self.method in ["validation_weighted", "confidence_weighted"]:
            # Inverse MSE weighting on validation set
            mses = {}
            for name, preds in val_predictions.items():
                mse = float(np.mean((preds - y_val) ** 2))
                mses[name] = max(mse, 1e-6)

            inv_mses = {name: 1.0 / mse for name, mse in mses.items()}
            total = sum(inv_mses.values())
            self.weights = {name: inv_mses[name] / total for name in inv_mses.keys()}

        return self.weights

    def predict(self, model_predictions: Dict[str, np.ndarray]) -> np.ndarray:
        """Combine model predictions using established weights."""
        if not self.weights:
            n = len(model_predictions)
            self.weights = {name: 1.0 / n for name in model_predictions.keys()}

        ensemble_pred = np.zeros(len(next(iter(model_predictions.values()))), dtype=float)
        for name, preds in model_predictions.items():
            w = self.weights.get(name, 1.0 / len(model_predictions))
            ensemble_pred += w * np.asarray(preds, dtype=float)

        return ensemble_pred
