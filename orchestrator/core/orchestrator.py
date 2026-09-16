"""
Central ResearchOrchestrator Facade for Phase 22 Pipeline Coordination.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

from orchestrator.schemas.workflow_schema import Workflow, Job, PolicyResult
from orchestrator.core.states import WorkflowStatus, TaskStatus, JobStatus
from orchestrator.workflows.workflow_builder import WorkflowBuilder
from orchestrator.dependencies.dag_validator import DAGValidator
from orchestrator.policies.policy_engine import ResearchPolicyEngine
from orchestrator.scheduler.job_queue import JobQueue
from orchestrator.executor.job_executor import JobExecutor
from orchestrator.resources.resource_monitor import ResourceMonitor
from orchestrator.state.checkpoint_manager import CheckpointManager
from orchestrator.recovery.failure_handler import FailureHandler, RetryPolicy
from orchestrator.events.event_bus import EventBus
from orchestrator.monitoring.workflow_monitor import WorkflowMonitor
from orchestrator.tasks.runner_tasks import (
    DataValidationTask,
    FeatureEngineeringTask,
    ModelTrainingTask,
    SignalGenerationTask,
    PortfolioConstructionTask,
    ExecutionSimulationTask,
    BacktestTask,
    RiskAnalysisTask,
    ResearchEvaluationTask,
    RobustnessTask,
    ReportGenerationTask,
)


class ResearchOrchestrator:
    """
    Central orchestrator coordinating quantitative research workflows, DAG execution,
    resource safety, validation gates, event bus, and checkpoint persistence.
    """

    TASK_CLASS_MAP = {
        "DataValidationTask": DataValidationTask,
        "FeatureEngineeringTask": FeatureEngineeringTask,
        "ModelTrainingTask": ModelTrainingTask,
        "SignalGenerationTask": SignalGenerationTask,
        "PortfolioConstructionTask": PortfolioConstructionTask,
        "ExecutionSimulationTask": ExecutionSimulationTask,
        "BacktestTask": BacktestTask,
        "RiskAnalysisTask": RiskAnalysisTask,
        "ResearchEvaluationTask": ResearchEvaluationTask,
        "RobustnessTask": RobustnessTask,
        "ReportGenerationTask": ReportGenerationTask,
    }

    def __init__(self, storage_dir: str = "artifacts/workflows"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

        self.policy_engine = ResearchPolicyEngine()
        self.event_bus = EventBus()
        self.checkpoint_manager = CheckpointManager(base_dir=self.storage_dir)
        self.executor = JobExecutor()
        self.failure_handler = FailureHandler(RetryPolicy(enabled=True, max_attempts=2))
        self.workflows: Dict[str, Workflow] = {}

    def create_workflow(
        self,
        name: str = "Multimodal Quant Research Workflow",
        template: str = "full_research",
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> Workflow:
        if template == "full_research":
            wf = WorkflowBuilder.build_full_research_workflow(name=name, custom_config=custom_config)
        else:
            # Fallback default
            wf = WorkflowBuilder.build_full_research_workflow(name=name, custom_config=custom_config)

        self.workflows[wf.workflow_id] = wf
        self._save_workflow(wf)
        self.event_bus.emit(
            event_type="workflow_created",
            workflow_id=wf.workflow_id,
            payload={"name": wf.name, "template": template},
        )
        return wf

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        if workflow_id in self.workflows:
            return self.workflows[workflow_id]
        filepath = os.path.join(self.storage_dir, workflow_id, "workflow.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                wf = Workflow(**data)
                self.workflows[workflow_id] = wf
                return wf
        return None

    def list_workflows(self) -> List[Dict[str, Any]]:
        wf_list = []
        if os.path.exists(self.storage_dir):
            for folder in os.listdir(self.storage_dir):
                filepath = os.path.join(self.storage_dir, folder, "workflow.json")
                if os.path.exists(filepath):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        wf_list.append({
                            "workflow_id": data["workflow_id"],
                            "name": data["name"],
                            "status": data["status"],
                            "tasks_count": len(data["tasks"]),
                            "completed_tasks_count": len(data.get("completed_tasks", [])),
                            "created_at": data.get("created_at"),
                        })
        return wf_list

    def validate_workflow(self, workflow_id: str) -> List[PolicyResult]:
        wf = self.get_workflow(workflow_id)
        if not wf:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        wf.status = WorkflowStatus.VALIDATING
        DAGValidator.validate_and_sort(wf.tasks)

        policy_results = self.policy_engine.evaluate_all(wf.configuration)
        has_failure = any(r.status == "FAIL" for r in policy_results)

        if has_failure:
            wf.status = WorkflowStatus.FAILED
            self.event_bus.emit(
                event_type="workflow_validation_failed",
                workflow_id=workflow_id,
                payload={"results": [r.dict() for r in policy_results]},
            )
        else:
            wf.status = WorkflowStatus.READY
            self.event_bus.emit(
                event_type="workflow_validated",
                workflow_id=workflow_id,
                payload={"status": "PASS"},
            )

        self._save_workflow(wf)
        return policy_results

    def start_workflow(self, workflow_id: str) -> Workflow:
        wf = self.get_workflow(workflow_id)
        if not wf:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        # Resource check
        ok, msg = ResourceMonitor.check_limits(wf.resource_budget, active_jobs_count=0)
        if not ok:
            wf.status = WorkflowStatus.FAILED
            self._save_workflow(wf)
            raise RuntimeError(f"Resource safety check failed: {msg}")

        wf.status = WorkflowStatus.RUNNING
        self.event_bus.emit(event_type="workflow_started", workflow_id=workflow_id)

        # Sort tasks topologically
        sorted_tasks = DAGValidator.validate_and_sort(wf.tasks)
        context = wf.configuration.copy()
        context["workflow_id"] = workflow_id

        queue = JobQueue()
        for task in sorted_tasks:
            if task.status != TaskStatus.COMPLETED:
                job = Job(
                    job_id=f"JOB-{task.task_id}",
                    task_id=task.task_id,
                    workflow_id=workflow_id,
                    priority=wf.priority,
                )
                queue.push(job)

        completed_set = set(wf.completed_tasks)

        while not queue.is_empty():
            if wf.status == WorkflowStatus.PAUSED:
                self.event_bus.emit(event_type="workflow_paused", workflow_id=workflow_id)
                self._save_workflow(wf)
                return wf

            if wf.status == WorkflowStatus.CANCELLED:
                self.event_bus.emit(event_type="workflow_cancelled", workflow_id=workflow_id)
                self._save_workflow(wf)
                return wf

            job = queue.pop()
            if not job:
                break

            task = next((t for t in sorted_tasks if t.task_id == job.task_id), None)
            if not task:
                continue

            # Check dependencies completed
            deps_ok = all(dep in completed_set for dep in task.depends_on)
            if not deps_ok:
                task.status = TaskStatus.FAILED
                task.error = f"Dependencies for '{task.task_id}' not satisfied"
                wf.status = WorkflowStatus.FAILED
                self.event_bus.emit(
                    event_type="task_failed",
                    workflow_id=workflow_id,
                    task_id=task.task_id,
                    payload={"error": task.error},
                )
                self._save_workflow(wf)
                return wf

            # Run task via executor
            task_cls = self.TASK_CLASS_MAP.get(task.task_type, DataValidationTask)
            task_inst = task_cls(task_id=task.task_id, name=task.name, configuration=task.configuration)

            task.status = TaskStatus.RUNNING
            self.event_bus.emit(event_type="task_started", workflow_id=workflow_id, task_id=task.task_id)

            updated_job, updated_ctx = self.executor.execute(job, task_inst, context)

            if updated_job.status == JobStatus.COMPLETED:
                task.status = TaskStatus.COMPLETED
                completed_set.add(task.task_id)
                wf.completed_tasks = list(completed_set)
                context = updated_ctx
                self.event_bus.emit(
                    event_type="task_completed",
                    workflow_id=workflow_id,
                    task_id=task.task_id,
                )
                # Checkpoint
                self.checkpoint_manager.save_checkpoint(wf, context)
            else:
                task.status = TaskStatus.FAILED
                task.error = updated_job.error
                wf.status = WorkflowStatus.FAILED
                self.event_bus.emit(
                    event_type="task_failed",
                    workflow_id=workflow_id,
                    task_id=task.task_id,
                    payload={"error": updated_job.error},
                )
                self._save_workflow(wf)
                return wf

        wf.status = WorkflowStatus.COMPLETED
        self.event_bus.emit(event_type="workflow_completed", workflow_id=workflow_id)
        self._save_workflow(wf)
        return wf

    def pause_workflow(self, workflow_id: str) -> Workflow:
        wf = self.get_workflow(workflow_id)
        if not wf:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        wf.status = WorkflowStatus.PAUSED
        self._save_workflow(wf)
        return wf

    def resume_workflow(self, workflow_id: str) -> Workflow:
        wf = self.get_workflow(workflow_id)
        if not wf:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        wf, restored_ctx = self.checkpoint_manager.resume_workflow(wf)
        wf.configuration.update(restored_ctx)
        self._save_workflow(wf)
        return self.start_workflow(workflow_id)

    def cancel_workflow(self, workflow_id: str) -> Workflow:
        wf = self.get_workflow(workflow_id)
        if not wf:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        wf.status = WorkflowStatus.CANCELLED
        self.event_bus.emit(event_type="workflow_cancelled", workflow_id=workflow_id)
        self._save_workflow(wf)
        return wf

    def retry_workflow(self, workflow_id: str) -> Workflow:
        wf = self.get_workflow(workflow_id)
        if not wf:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        # Reset failed tasks
        for t in wf.tasks:
            if t.status == TaskStatus.FAILED:
                t.status = TaskStatus.PENDING
                t.error = None
        wf.status = WorkflowStatus.READY
        self._save_workflow(wf)
        return self.start_workflow(workflow_id)

    def get_events(self, workflow_id: str) -> List[Dict[str, Any]]:
        return self.event_bus.get_events(workflow_id)

    def get_health(self) -> Dict[str, Any]:
        return WorkflowMonitor.get_health_status()

    def _save_workflow(self, workflow: Workflow):
        wf_dir = os.path.join(self.storage_dir, workflow.workflow_id)
        os.makedirs(wf_dir, exist_ok=True)
        filepath = os.path.join(wf_dir, "workflow.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(workflow.model_dump_json(indent=2))
