"""
Workflow Checkpoint Manager for Safe Stage Persistence & Resume.
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
from orchestrator.schemas.workflow_schema import Workflow
from orchestrator.core.states import TaskStatus, WorkflowStatus


class CheckpointManager:
    """
    Saves and restores workflow execution state to artifacts/workflows/<workflow_id>/checkpoint.json.
    Allows workflow resume by skipping safe completed tasks.
    """

    def __init__(self, base_dir: str = "artifacts/workflows"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_checkpoint_path(self, workflow_id: str) -> str:
        wf_dir = os.path.join(self.base_dir, workflow_id)
        os.makedirs(wf_dir, exist_ok=True)
        return os.path.join(wf_dir, "checkpoint.json")

    def save_checkpoint(self, workflow: Workflow, context: Dict[str, Any]) -> str:
        filepath = self._get_checkpoint_path(workflow.workflow_id)
        data = {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status.value,
            "completed_tasks": workflow.completed_tasks,
            "context": context,
            "tasks_status": {t.task_id: t.status.value for t in workflow.tasks},
        }
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2))
        return filepath

    def load_checkpoint(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        filepath = self._get_checkpoint_path(workflow_id)
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def resume_workflow(self, workflow: Workflow) -> Tuple[Workflow, Dict[str, Any]]:
        checkpoint = self.load_checkpoint(workflow.workflow_id)
        if not checkpoint:
            return workflow, workflow.configuration.copy()

        context = checkpoint.get("context", workflow.configuration.copy())
        completed = set(checkpoint.get("completed_tasks", []))
        tasks_status = checkpoint.get("tasks_status", {})

        workflow.completed_tasks = list(completed)

        for task in workflow.tasks:
            if task.task_id in completed or tasks_status.get(task.task_id) == TaskStatus.COMPLETED.value:
                task.status = TaskStatus.COMPLETED

        workflow.status = WorkflowStatus.READY
        return workflow, context
