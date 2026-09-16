"""
State Manager for Pipeline and Stage Lifecycles.
Tracks execution states, timestamps, stage statuses, and duration statistics.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
import datetime
from orchestration.dependency_graph import PipelineStage


class PipelineState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class StageState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class StageRecord:
    stage: PipelineStage
    status: StageState = StageState.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["stage"] = self.stage.value
        data["status"] = self.status.value
        return data


@dataclass
class PipelineRunState:
    run_id: str
    experiment_id: str
    status: PipelineState = PipelineState.PENDING
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_duration_seconds: float = 0.0
    stage_records: Dict[str, StageRecord] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.stage_records:
            for s in PipelineStage:
                self.stage_records[s.value] = StageRecord(stage=s)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_duration_seconds": self.total_duration_seconds,
            "stages": {k: v.to_dict() for k, v in self.stage_records.items()},
            "metadata": self.metadata,
        }


class StateManager:
    """Manages state transitions for active pipeline runs and stage executions."""

    def __init__(self):
        self._runs: Dict[str, PipelineRunState] = {}

    def create_run_state(self, run_id: str, experiment_id: str, metadata: Optional[Dict[str, Any]] = None) -> PipelineRunState:
        state = PipelineRunState(run_id=run_id, experiment_id=experiment_id, metadata=metadata or {})
        self._runs[run_id] = state
        return state

    def get_run_state(self, run_id: str) -> Optional[PipelineRunState]:
        return self._runs.get(run_id)

    def start_pipeline(self, run_id: str):
        state = self._runs.get(run_id)
        if state:
            state.status = PipelineState.RUNNING
            state.started_at = datetime.datetime.utcnow().isoformat()

    def start_stage(self, run_id: str, stage: PipelineStage):
        state = self._runs.get(run_id)
        if state and stage.value in state.stage_records:
            rec = state.stage_records[stage.value]
            rec.status = StageState.RUNNING
            rec.started_at = datetime.datetime.utcnow().isoformat()

    def complete_stage(self, run_id: str, stage: PipelineStage, duration: float = 0.0):
        state = self._runs.get(run_id)
        if state and stage.value in state.stage_records:
            rec = state.stage_records[stage.value]
            rec.status = StageState.COMPLETED
            rec.completed_at = datetime.datetime.utcnow().isoformat()
            rec.duration_seconds = duration

    def fail_stage(self, run_id: str, stage: PipelineStage, error: str, stack_trace: Optional[str] = None):
        state = self._runs.get(run_id)
        if state and stage.value in state.stage_records:
            rec = state.stage_records[stage.value]
            rec.status = StageState.FAILED
            rec.completed_at = datetime.datetime.utcnow().isoformat()
            rec.error_message = error
            rec.stack_trace = stack_trace
            state.status = PipelineState.FAILED
            state.completed_at = datetime.datetime.utcnow().isoformat()

    def complete_pipeline(self, run_id: str, duration: float = 0.0):
        state = self._runs.get(run_id)
        if state:
            state.status = PipelineState.COMPLETED
            state.completed_at = datetime.datetime.utcnow().isoformat()
            state.total_duration_seconds = duration
