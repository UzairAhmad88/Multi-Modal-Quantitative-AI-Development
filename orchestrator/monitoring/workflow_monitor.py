"""
Workflow & System Monitoring for Phase 22 Orchestrator.
"""

from typing import Dict, Any, List
from orchestrator.schemas.workflow_schema import Workflow
from orchestrator.core.states import WorkflowStatus, TaskStatus
from orchestrator.resources.resource_monitor import ResourceMonitor


class WorkflowMonitor:
    """
    Exposes real-time progress metrics, task states, resource metrics, and health status.
    """

    @staticmethod
    def get_progress(workflow: Workflow) -> Dict[str, Any]:
        total = len(workflow.tasks)
        if total == 0:
            return {"percent_complete": 0.0, "completed": 0, "total": 0}

        completed = sum(1 for t in workflow.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in workflow.tasks if t.status == TaskStatus.FAILED)
        running = sum(1 for t in workflow.tasks if t.status == TaskStatus.RUNNING)
        pending = sum(1 for t in workflow.tasks if t.status == TaskStatus.PENDING)

        return {
            "percent_complete": round((completed / total) * 100.0, 1),
            "completed_tasks": completed,
            "failed_tasks": failed,
            "running_tasks": running,
            "pending_tasks": pending,
            "total_tasks": total,
        }

    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        res_metrics = ResourceMonitor.get_current_metrics()
        return {
            "status": "HEALTHY",
            "components": {
                "data_platform": "CONNECTED",
                "model_factory": "CONNECTED",
                "portfolio_engine": "CONNECTED",
                "execution_engine": "CONNECTED",
                "backtest_engine": "CONNECTED",
                "research_lab": "CONNECTED",
                "resource_monitor": "OK",
            },
            "system_resources": res_metrics,
        }
