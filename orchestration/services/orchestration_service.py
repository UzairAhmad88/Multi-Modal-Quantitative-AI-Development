"""
Unified Orchestration Service managing pipeline runs and REST endpoints.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..pipeline import ResearchPipelineEngine
from ..pipeline_state import PipelineRunState


class OrchestrationService:
    """Service layer for running, listing, resuming, and managing pipeline runs."""

    def __init__(self, artifacts_dir: Optional[str] = None):
        if artifacts_dir is None:
            artifacts_dir = os.path.join(os.getcwd(), "artifacts", "orchestration")
        self.artifacts_dir = Path(artifacts_dir)
        self.engine = ResearchPipelineEngine(checkpoints_dir=str(self.artifacts_dir / "checkpoints"))

    def run_pipeline(
        self,
        experiment_id: str = "EXP-END2END-001",
        symbols: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> PipelineRunState:
        return self.engine.run_pipeline(
            experiment_id=experiment_id,
            symbols=symbols,
            config=config,
        )

    def resume_pipeline(self, run_id: str) -> PipelineRunState:
        state = self.engine.checkpoint_mgr.load_checkpoint(run_id)
        exp_id = state.experiment_id if state else "EXP-RESUME"
        return self.engine.run_pipeline(
            experiment_id=exp_id,
            resume_run_id=run_id,
        )

    def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        state = self.engine.checkpoint_mgr.load_checkpoint(run_id)
        if not state:
            return None
        return state.model_dump()

    def list_pipeline_runs(self) -> List[Dict[str, Any]]:
        runs = []
        chk_dir = self.artifacts_dir / "checkpoints"
        if not chk_dir.exists():
            return runs

        for f in sorted(chk_dir.glob("*.json"), key=os.path.getmtime, reverse=True):
            try:
                with open(f, "r") as fp:
                    data = json.load(fp)
                    runs.append({
                        "run_id": data.get("run_id"),
                        "experiment_id": data.get("experiment_id"),
                        "status": data.get("status"),
                        "duration_seconds": data.get("duration_seconds"),
                        "completed_stages_count": len(data.get("completed_stages", [])),
                    })
            except Exception:
                continue
        return runs
