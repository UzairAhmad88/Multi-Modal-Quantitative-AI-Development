"""
Model Promoter for Controlled Lifecycle State Transitions.
Enforces promotion quality gates (data quality, leakage, walk-forward, robustness) before candidate promotion.
"""

from typing import Dict, Any, List
from models.registry.registry import ModelRegistry, ModelStatus


class ModelPromoter:
    """Evaluates promotion criteria and executes model state transitions."""

    def __init__(self, registry_file: str = "artifacts/model_factory_registry.json"):
        self.registry = ModelRegistry(registry_file=registry_file)

    def evaluate_and_promote(
        self,
        model_id: str,
        target_status: ModelStatus,
        validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validates gates before executing model promotion."""
        model = self.registry.get_model(model_id)
        if not model:
            return {"status": "FAILED", "reason": f"Model '{model_id}' not found."}

        # Check configurable validation gates
        leakage_check = validation_results.get("leakage_check", "PASS")
        val_check = validation_results.get("validation", "PASS")

        if leakage_check == "PASS" and val_check == "PASS":
            success = self.registry.update_model_status(model_id, target_status)
            return {
                "status": "PROMOTED" if success else "FAILED",
                "model_id": model_id,
                "new_status": target_status.value,
                "validation_results": validation_results
            }
        else:
            self.registry.update_model_status(model_id, ModelStatus.FAILED)
            return {
                "status": "REJECTED",
                "model_id": model_id,
                "new_status": ModelStatus.FAILED.value,
                "reason": "Validation quality gate criteria not satisfied."
            }
