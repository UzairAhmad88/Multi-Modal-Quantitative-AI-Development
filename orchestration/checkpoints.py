"""
JSON Checkpoint Persistence Manager for Orchestration OS.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from .pipeline_state import PipelineRunState


class CheckpointManager:
    """Manages reading and writing pipeline run checkpoints."""

    def __init__(self, checkpoints_dir: Optional[str] = None):
        if checkpoints_dir is None:
            checkpoints_dir = os.path.join(os.getcwd(), "artifacts", "orchestration", "checkpoints")
        self.checkpoints_dir = Path(checkpoints_dir)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, state: PipelineRunState) -> str:
        filepath = self.checkpoints_dir / f"{state.run_id}.json"
        with open(filepath, "w") as f:
            f.write(state.model_dump_json(indent=2))
        return str(filepath)

    def load_checkpoint(self, run_id: str) -> Optional[PipelineRunState]:
        filepath = self.checkpoints_dir / f"{run_id}.json"
        if not filepath.exists():
            return None
        with open(filepath, "r") as f:
            return PipelineRunState.model_validate_json(f.read())
