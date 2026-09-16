"""
Experiment Manager for Research Intelligence.
Handles experiment creation, queuing, priority sorting, resource limits, human approval enforcement,
and diagnostics recording for failed runs.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
import datetime
import os
import sys
import platform
import uuid


class ExperimentPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class ExperimentStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class ResourceLimits:
    max_cpu: int = 4
    max_memory_gb: float = 8.0
    max_parallel_jobs: int = 2
    max_training_time_sec: int = 600


@dataclass
class ExperimentVersions:
    experiment_version: str = "1.0.0"
    code_version: str = "1.0.0"
    dataset_version: str = "v1"
    feature_version: str = "v1"
    model_version: str = "v1"
    config_version: str = "v1"


@dataclass
class ExperimentConfig:
    name: str
    hypothesis_id: str
    dataset: str
    features: List[str]
    model: str
    validation: Dict[str, Any] = field(default_factory=dict)
    backtest: Dict[str, Any] = field(default_factory=dict)
    portfolio: Dict[str, Any] = field(default_factory=dict)
    risk: Dict[str, Any] = field(default_factory=dict)
    random_seed: int = 42
    versions: ExperimentVersions = field(default_factory=ExperimentVersions)
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)


@dataclass
class FailedExperimentDiagnostics:
    error_type: str
    error_message: str
    stack_trace: str
    stage: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    environment: Dict[str, str] = field(default_factory=lambda: {
        "python": sys.version,
        "os": platform.platform(),
        "cpu_count": str(os.cpu_count()),
    })


@dataclass
class ExperimentRecord:
    experiment_id: str
    config: ExperimentConfig
    priority: ExperimentPriority = ExperimentPriority.NORMAL
    status: ExperimentStatus = ExperimentStatus.QUEUED
    approved_by_human: bool = False
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    results: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Optional[FailedExperimentDiagnostics] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "name": self.config.name,
            "hypothesis_id": self.config.hypothesis_id,
            "dataset": self.config.dataset,
            "features": self.config.features,
            "model": self.config.model,
            "priority": self.priority.value,
            "status": self.status.value,
            "approved_by_human": self.approved_by_human,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "results": self.results,
            "diagnostics": asdict(self.diagnostics) if self.diagnostics else None,
        }


class IntelExperimentManager:
    """Manages creation, queueing, priority ordering, and state transitions of experiments."""

    def __init__(self):
        self._experiments: Dict[str, ExperimentRecord] = {}
        self._sequence_counter: int = 1

    def create_experiment(
        self,
        config: ExperimentConfig,
        priority: ExperimentPriority = ExperimentPriority.NORMAL,
        auto_approve: bool = False,
    ) -> ExperimentRecord:
        exp_id = f"EXP-{datetime.date.today().year}-{self._sequence_counter:06d}"
        self._sequence_counter += 1

        record = ExperimentRecord(
            experiment_id=exp_id,
            config=config,
            priority=priority,
            status=ExperimentStatus.QUEUED,
            approved_by_human=auto_approve,
        )
        self._experiments[exp_id] = record
        return record

    def approve_experiment(self, experiment_id: str) -> bool:
        record = self._experiments.get(experiment_id)
        if not record:
            return False
        record.approved_by_human = True
        return True

    def get_queued_experiments(self) -> List[ExperimentRecord]:
        """Returns queued experiments sorted by priority (HIGH > NORMAL > LOW) then creation order."""
        priority_map = {
            ExperimentPriority.HIGH: 3,
            ExperimentPriority.NORMAL: 2,
            ExperimentPriority.LOW: 1,
        }
        queued = [e for e in self._experiments.values() if e.status == ExperimentStatus.QUEUED and e.approved_by_human]
        queued.sort(key=lambda x: priority_map[x.priority], reverse=True)
        return queued

    def get(self, experiment_id: str) -> Optional[ExperimentRecord]:
        return self._experiments.get(experiment_id)

    def list_all(self) -> List[ExperimentRecord]:
        return list(self._experiments.values())

    def record_failure(
        self, experiment_id: str, stage: str, error_type: str, error_message: str, stack_trace: str
    ):
        record = self._experiments.get(experiment_id)
        if not record:
            return
        record.status = ExperimentStatus.FAILED
        record.completed_at = datetime.datetime.utcnow().isoformat()
        record.diagnostics = FailedExperimentDiagnostics(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            stage=stage,
        )

    def record_success(self, experiment_id: str, results: Dict[str, Any]):
        record = self._experiments.get(experiment_id)
        if not record:
            return
        record.status = ExperimentStatus.COMPLETED
        record.completed_at = datetime.datetime.utcnow().isoformat()
        record.results = results
