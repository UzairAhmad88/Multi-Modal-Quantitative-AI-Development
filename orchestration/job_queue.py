"""
Job Queue for Research Experiment Runs.
Schedules priority-sorted execution queues for research jobs.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
import datetime


class JobPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class JobRecord:
    job_id: str
    run_id: str
    experiment_id: str
    config_path: str
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.QUEUED
    queued_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        return data


class JobQueue:
    """Priority queue for research jobs."""

    def __init__(self):
        self._jobs: Dict[str, JobRecord] = {}

    def enqueue(
        self, run_id: str, experiment_id: str, config_path: str, priority: JobPriority = JobPriority.NORMAL
    ) -> JobRecord:
        job_id = f"JOB-{run_id}"
        job = JobRecord(
            job_id=job_id,
            run_id=run_id,
            experiment_id=experiment_id,
            config_path=config_path,
            priority=priority,
        )
        self._jobs[job_id] = job
        return job

    def pop_next_job(self) -> Optional[JobRecord]:
        priority_order = {JobPriority.HIGH: 3, JobPriority.NORMAL: 2, JobPriority.LOW: 1}
        queued = [j for j in self._jobs.values() if j.status == JobStatus.QUEUED]
        if not queued:
            return None
        queued.sort(key=lambda x: priority_order[x.priority], reverse=True)
        next_job = queued[0]
        next_job.status = JobStatus.RUNNING
        next_job.started_at = datetime.datetime.utcnow().isoformat()
        return next_job

    def list_jobs(self) -> List[JobRecord]:
        return list(self._jobs.values())
