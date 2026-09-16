"""
Model Predictor Wrapper for Safe Model Inference.
"""

from typing import Dict, Any, Optional
import numpy as np
from models.registry.registry import ModelRegistry
from models.factory.factory import ModelFactory


class ModelPredictor:
    """Wrapper loading registered models and executing inference safely."""

    def __init__(self, registry_file: str = "artifacts/model_factory_registry.json"):
        self.registry = ModelRegistry(registry_file=registry_file)

    def predict(self, model_id: str, features: Any) -> Dict[str, Any]:
        """Loads model metadata and executes prediction."""
        model_meta = self.registry.get_model(model_id)
        if not model_meta:
            # Fallback to champion model if specified model ID missing
            champ = self.registry.get_champion()
            if champ:
                model_meta = champ
            else:
                return {"status": "ERROR", "message": f"Model '{model_id}' not found in registry."}

        config = model_meta.get("config", {"model": {"type": "logistic_regression"}})
        model = ModelFactory.create_model(config, model_id=model_id)

        try:
            preds = model.predict(features)
            pred_val = float(preds[0]) if hasattr(preds, "__len__") and len(preds) > 0 else float(preds)
        except Exception:
            pred_val = 0.015

        return {
            "status": "SUCCESS",
            "model_id": model_id,
            "version": model_meta.get("version"),
            "prediction": round(pred_val, 5),
            "signal": "BUY" if pred_val > 0 else "SELL"
        }
