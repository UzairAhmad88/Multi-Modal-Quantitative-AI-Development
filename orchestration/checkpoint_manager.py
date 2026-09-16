"""
Checkpoint Manager for Research Pipeline Stage Serialization.
Saves and restores stage output checkpoints to enable zero-recomputation resume executions.
"""

import os
import json
from typing import Dict, Any, Optional
from orchestration.dependency_graph import PipelineStage


class CheckpointManager:
    """Saves and restores JSON stage checkpoints under artifacts/EXP-xxxx/checkpoints/."""

    def __init__(self, base_artifact_dir: str = "artifacts"):
        self.base_artifact_dir = base_artifact_dir

    def _get_checkpoint_dir(self, experiment_id: str) -> str:
        d = os.path.join(self.base_artifact_dir, f"experiments/{experiment_id}/checkpoints")
        os.makedirs(d, exist_ok=True)
        return d

    def save_checkpoint(self, experiment_id: str, stage: PipelineStage, data: Dict[str, Any]) -> str:
        checkpoint_dir = self._get_checkpoint_dir(experiment_id)
        filename = f"{stage.value.lower()}.json"
        filepath = os.path.join(checkpoint_dir, filename)

        payload = {
            "experiment_id": experiment_id,
            "stage": stage.value,
            "data": data,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return filepath

    def load_checkpoint(self, experiment_id: str, stage: PipelineStage) -> Optional[Dict[str, Any]]:
        checkpoint_dir = self._get_checkpoint_dir(experiment_id)
        filename = f"{stage.value.lower()}.json"
        filepath = os.path.join(checkpoint_dir, filename)

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                payload = json.load(f)
            return payload.get("data")
        except Exception:
            return None

    def has_checkpoint(self, experiment_id: str, stage: PipelineStage) -> bool:
        return self.load_checkpoint(experiment_id, stage) is not None
