"""
Stage Failure Recovery Engine for Orchestration OS.
"""

from typing import List, Optional
from .checkpoints import CheckpointManager
from .pipeline_state import PipelineRunState, StageStatus


class RecoveryEngine:
    """Manages checkpoint recovery and stage re-execution selection."""

    def __init__(self, checkpoint_mgr: CheckpointManager):
        self.checkpoint_mgr = checkpoint_mgr

    def get_resume_stages(self, run_id: str, all_stages: List[str]) -> List[str]:
        state = self.checkpoint_mgr.load_checkpoint(run_id)
        if not state:
            return list(all_stages)

        stages_to_run = []
        for s in all_stages:
            st_state = state.stages.get(s)
            if not st_state or st_state.status != StageStatus.COMPLETED:
                stages_to_run.append(s)

        return stages_to_run
