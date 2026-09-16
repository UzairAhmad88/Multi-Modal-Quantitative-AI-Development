"""
Pipeline Event Emitter and Event Store for Orchestration OS.
"""

import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PipelineEventType(str, Enum):
    PIPELINE_STARTED = "PIPELINE_STARTED"
    STAGE_STARTED = "STAGE_STARTED"
    STAGE_COMPLETED = "STAGE_COMPLETED"
    STAGE_FAILED = "STAGE_FAILED"
    CHECKPOINT_CREATED = "CHECKPOINT_CREATED"
    LEAKAGE_DETECTED = "LEAKAGE_DETECTED"
    RISK_BREACH = "RISK_BREACH"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    PIPELINE_COMPLETED = "PIPELINE_COMPLETED"


class PipelineEvent(BaseModel):
    event_id: str
    run_id: str
    experiment_id: str
    event_type: PipelineEventType
    stage_name: Optional[str] = None
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    details: Dict[str, Any] = Field(default_factory=dict)


class EventEmitter:
    """Collects and dispatches pipeline events."""

    def __init__(self):
        self._events: List[PipelineEvent] = []

    def emit(
        self,
        event_id: str,
        run_id: str,
        experiment_id: str,
        event_type: PipelineEventType,
        message: str,
        stage_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> PipelineEvent:
        event = PipelineEvent(
            event_id=event_id,
            run_id=run_id,
            experiment_id=experiment_id,
            event_type=event_type,
            stage_name=stage_name,
            message=message,
            details=details or {},
        )
        self._events.append(event)
        return event

    def get_events(self, run_id: Optional[str] = None) -> List[PipelineEvent]:
        if run_id is None:
            return list(self._events)
        return [e for e in self._events if e.run_id == run_id]
