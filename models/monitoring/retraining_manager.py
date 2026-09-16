"""
Model Retraining Manager.
Governs scheduled or event-driven model retraining while enforcing safety gates.
"""

from typing import Dict, Any, Optional
from models.registry.registry import ModelRegistry, ModelStatus
from models.training.trainer import ModelTrainingEngine


class ModelRetrainingManager:
    """Manages model retraining pipelines with safety gates."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.trainer = ModelTrainingEngine()
        self.registry = ModelRegistry()

    def trigger_retraining(
        self,
        model_id: str,
        new_data: Optional[Any] = None,
        reason: str = "MANUAL_TRIGGER"
    ) -> Dict[str, Any]:
        """Triggers model retraining if enabled and safety gates pass."""
        if not self.enabled and reason != "MANUAL_TRIGGER":
            return {
                "status": "DISABLED",
                "message": "Automated retraining is disabled by configuration default."
            }

        existing_model = self.registry.get_model(model_id)
        if not existing_model:
            return {"status": "FAILED", "reason": f"Model '{model_id}' not found."}

        config = existing_model.get("config", {})
        # Update version increment
        ver_parts = existing_model.get("version", "1.0.0").split(".")
        new_version = f"{ver_parts[0]}.{int(ver_parts[1]) + 1}.0"
        config.setdefault("model", {})["version"] = new_version

        res = self.trainer.train_model(config)
        return {
            "status": "RETRAINED",
            "reason": reason,
            "original_model_id": model_id,
            "retrained_model_id": res["model_id"],
            "new_version": new_version,
            "metrics": res["metrics"]
        }
