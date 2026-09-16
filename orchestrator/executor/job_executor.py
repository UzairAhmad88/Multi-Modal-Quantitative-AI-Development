"""
Job Executor for Subprocess / Function Task Execution.
"""

import os
import time
import trace
import logging
from typing import Dict, Any, Tuple
from datetime import datetime

from orchestrator.schemas.workflow_schema import Job
from orchestrator.core.states import JobStatus
from orchestrator.tasks.base_task import BaseTask


class JobExecutor:
    """
    Executes single pipeline tasks locally with log capture, timing, and error handling.
    """

    def __init__(self, log_dir: str = "logs/workflows"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def execute(self, job: Job, task: BaseTask, context: Dict[str, Any]) -> Tuple[Job, Dict[str, Any]]:
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow().isoformat()
        
        task_log_dir = os.path.join(self.log_dir, job.workflow_id, "tasks")
        os.makedirs(task_log_dir, exist_ok=True)
        log_file = os.path.join(task_log_dir, f"{job.task_id}.log")
        job.log_file = log_file

        start_time = time.time()

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.utcnow().isoformat()}] Starting task '{task.task_id}' ({task.name})\n")
                
                # 1. Gate validation
                if not task.validate(context):
                    msg = f"Task '{task.task_id}' failed pre-execution gate validation"
                    f.write(f"[{datetime.utcnow().isoformat()}] ERROR: {msg}\n")
                    job.status = JobStatus.FAILED
                    job.error = msg
                    job.completed_at = datetime.utcnow().isoformat()
                    job.duration_seconds = time.time() - start_time
                    return job, context

                # 2. Task execution
                context = task.run(context)
                f.write(f"[{datetime.utcnow().isoformat()}] Task '{task.task_id}' completed successfully\n")

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow().isoformat()
            job.duration_seconds = time.time() - start_time
            return job, context

        except Exception as e:
            err_msg = str(e)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.utcnow().isoformat()}] EXCEPTION: {err_msg}\n")

            job.status = JobStatus.FAILED
            job.error = err_msg
            job.completed_at = datetime.utcnow().isoformat()
            job.duration_seconds = time.time() - start_time
            return job, context
