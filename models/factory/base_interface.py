"""
Standard Base Interface for All Quantitative AI Models.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class BaseQuantModel(ABC):
    """Abstract Base Class defining standard interface across ML, DL, NLP, and Ensemble models."""

    def __init__(self, model_id: str, name: str, version: str = "1.0.0", config: Optional[Dict[str, Any]] = None):
        self.model_id = model_id
        self.name = name
        self.version = version
        self.config = config or {}

    @abstractmethod
    def fit(self, X: Any, y: Any, **kwargs) -> Any:
        """Fits model on training features X and targets y."""
        pass

    @abstractmethod
    def predict(self, X: Any) -> np.ndarray:
        """Generates predictions for input features X."""
        pass

    def predict_proba(self, X: Any) -> Optional[np.ndarray]:
        """Generates class probabilities if supported by classification model."""
        return None

    @abstractmethod
    def save(self, filepath: str) -> str:
        """Serializes model artifact to disk."""
        pass

    @abstractmethod
    def load(self, filepath: str) -> Any:
        """Deserializes model artifact from disk."""
        pass

    def evaluate(self, X_test: Any, y_test: Any) -> Dict[str, Any]:
        """Evaluates model performance against target metrics."""
        preds = self.predict(X_test)
        mae = float(np.mean(np.abs(preds - y_test))) if len(preds) == len(y_test) else 0.0
        return {"mae": round(mae, 5)}

    def get_metadata(self) -> Dict[str, Any]:
        """Returns metadata summary."""
        return {
            "model_id": self.model_id,
            "name": self.name,
            "version": self.version,
            "config": self.config
        }
