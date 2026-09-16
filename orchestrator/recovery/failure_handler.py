"""
Failure Handler & Retry Policy Engine.
"""

from typing import Dict, Any, Tuple
from orchestrator.schemas.workflow_schema import WorkflowTask
from orchestrator.core.states import TaskStatus


class RetryPolicy:
    def __init__(self, enabled: bool = True, max_attempts: int = 2):
        self.enabled = enabled
        self.max_attempts = max_attempts


class FailureHandler:
    """
    Manages task failure state, logging, and retry logic for idempotent pipeline tasks.
    """

    def __init__(self, policy: RetryPolicy = None):
        self.policy = policy or RetryPolicy()

    def handle_failure(
        self,
        task: WorkflowTask,
        attempt: int,
        error_msg: str,
        context: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Returns (should_retry: bool, reason: str).
        """
        if not self.policy.enabled:
            task.status = TaskStatus.FAILED
            task.error = error_msg
            return False, "Retry policy is disabled"

        if attempt < self.policy.max_attempts:
            task.status = TaskStatus.PENDING
            return True, f"Attempt {attempt}/{self.policy.max_attempts} failed. Retrying task..."
        
        task.status = TaskStatus.FAILED
        task.error = error_msg
        return False, f"Max retry attempts ({self.policy.max_attempts}) reached"
