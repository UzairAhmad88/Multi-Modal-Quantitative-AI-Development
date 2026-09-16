"""
Pipeline Status and Stage State Tracking for Orchestration OS.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PipelineStatus(str, Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PARTIAL = "PARTIAL"


class StageStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class StageState(BaseModel):
    stage_name: str
    status: StageStatus = StageStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    artifacts: Dict[str, str] = Field(default_factory=dict)
    error_message: Optional[str] = None


class PipelineRunState(BaseModel):
    run_id: str
    experiment_id: str
    status: PipelineStatus = PipelineStatus.CREATED
    current_stage: Optional[str] = None
    stages: Dict[str, StageState] = Field(default_factory=dict)
    completed_stages: List[str] = Field(default_factory=list)
    failed_stage: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
