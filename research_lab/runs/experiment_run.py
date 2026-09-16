"""
Experiment Run Data Model: Tracks individual execution runs of an experiment.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import platform
import sys
from research_lab.experiments.states import RunStatus


@dataclass
class ExperimentRun:
    run_id: str = field(default_factory=lambda: f"RUN-{uuid.uuid4().hex[:8].upper()}")
    experiment_id: str = "EXP-001"
    random_seed: int = 42
    status: RunStatus = RunStatus.QUEUED
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    host_info: Dict[str, Any] = field(default_factory=lambda: {
        "platform": platform.platform(),
        "python_version": sys.version.split()[0]
    })
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    error_log: Optional[str] = None

    def complete_run(self, metrics: Dict[str, float], artifacts: Dict[str, str]):
        self.status = RunStatus.COMPLETED
        self.end_time = datetime.utcnow().isoformat() + "Z"
        self.metrics = metrics
        self.artifacts = artifacts

    def fail_run(self, error: str):
        self.status = RunStatus.FAILED
        self.end_time = datetime.utcnow().isoformat() + "Z"
        self.error_log = error

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value if hasattr(self.status, "value") else str(self.status)
        return data
