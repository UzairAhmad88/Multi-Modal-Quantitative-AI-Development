"""
Model Health Monitor for Dashboard Monitoring Feeds.
Aggregates health status across active paper models.
"""

from typing import Dict, Any, List
from models.registry.registry import ModelRegistry, ModelStatus


class ModelHealthMonitor:
    """Aggregates active model health status."""

    def __init__(self, registry_file: str = "artifacts/model_factory_registry.json"):
        self.registry = ModelRegistry(registry_file=registry_file)

    def get_system_health(self) -> Dict[str, Any]:
        champion = self.registry.get_champion()
        all_models = self.registry.list_models()

        return {
            "total_models": len(all_models),
            "active_champion": champion.get("model_id") if champion else "NONE",
            "champion_status": champion.get("status") if champion else "NO_CHAMPION",
            "candidates_count": len([m for m in all_models if m.get("status") == ModelStatus.CANDIDATE.value]),
            "archived_count": len([m for m in all_models if m.get("status") == ModelStatus.ARCHIVED.value]),
            "system_status": "HEALTHY" if champion else "ATTENTION_REQUIRED"
        }
