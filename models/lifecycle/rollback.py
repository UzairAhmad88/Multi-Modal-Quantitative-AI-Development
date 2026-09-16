"""
Model Rollback Manager for Restoring Previously Validated Models.
"""

from typing import Dict, Any, Optional
from models.registry.registry import ModelRegistry, ModelStatus


class ModelRollbackManager:
    """Manages champion model rollback to previous valid candidates."""

    def __init__(self, registry_file: str = "artifacts/model_factory_registry.json"):
        self.registry = ModelRegistry(registry_file=registry_file)

    def rollback(self) -> Dict[str, Any]:
        """Rolls back paper champion model to previous candidate."""
        curr_champ = self.registry.get_champion()
        restored = self.registry.rollback_champion()

        if restored:
            return {
                "status": "SUCCESS",
                "previous_champion": curr_champ.get("model_id") if curr_champ else None,
                "restored_champion": restored["model_id"],
                "version": restored["version"]
            }
        else:
            return {
                "status": "FAILED",
                "reason": "No valid previous candidate model available for rollback."
            }
