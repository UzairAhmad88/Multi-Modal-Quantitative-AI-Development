"""
Schemas for Workflow, Research Plan, Resource Budget, Job, and Policy Result.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from orchestrator.core.states import WorkflowStatus, JobStatus, TaskStatus, Priority


class ResourceBudget(BaseModel):
    max_experiments: int = 20
    max_parallel_jobs: int = 2
    max_runtime_minutes: int = 240
    max_memory_gb: int = 12


class WorkflowTask(BaseModel):
    task_id: str
    name: str
    task_type: str
    depends_on: List[str] = Field(default_factory=list)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    artifacts: List[str] = Field(default_factory=list)


class Workflow(BaseModel):
    workflow_id: str
    name: str
    objective: str
    experiment_template: str = "multimodal"
    status: WorkflowStatus = WorkflowStatus.DRAFT
    priority: Priority = Priority.NORMAL
    tasks: List[WorkflowTask] = Field(default_factory=list)
    resource_budget: ResourceBudget = Field(default_factory=ResourceBudget)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_tasks: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResearchPlan(BaseModel):
    plan_id: str
    name: str
    objective: str
    hypothesis: str
    dataset_id: str
    models: List[str] = Field(default_factory=lambda: ["xgboost", "lstm", "transformer"])
    modalities: List[str] = Field(default_factory=lambda: ["market", "market_news", "all"])
    strategies: List[str] = Field(default_factory=lambda: ["long_short", "trend"])
    executions: List[str] = Field(default_factory=lambda: ["twap", "vwap"])
    resource_budget: ResourceBudget = Field(default_factory=ResourceBudget)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Job(BaseModel):
    job_id: str
    task_id: str
    workflow_id: str
    experiment_id: Optional[str] = None
    run_id: Optional[str] = None
    status: JobStatus = JobStatus.QUEUED
    priority: Priority = Priority.NORMAL
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None
    log_file: Optional[str] = None


class PolicyResult(BaseModel):
    policy: str
    status: str  # PASS or FAIL
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
