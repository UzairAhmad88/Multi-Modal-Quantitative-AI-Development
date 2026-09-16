"""
Retry Manager for Stage Execution.
Manages retry policies and prevents unsafe repetition of deterministic validation failures.
"""

from typing import Dict, Any, Callable
import time
from orchestration.dependency_graph import PipelineStage


class RetryManager:
    """Manages stage execution retries with safety filters."""

    NON_RETRYABLE_STAGES = [
        PipelineStage.DATA_VALIDATION,
        PipelineStage.VALIDATION,
        PipelineStage.STATISTICAL_ANALYSIS,
    ]

    def __init__(self, enabled: bool = True, max_attempts: int = 3, backoff_seconds: float = 1.0):
        self.enabled = enabled
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds

    def is_retryable(self, stage: PipelineStage, exception: Exception) -> bool:
        if not self.enabled:
            return False
        if stage in self.NON_RETRYABLE_STAGES:
            return False
        if isinstance(exception, (ValueError, PermissionError)):
            return False
        return True

    def execute_with_retry(
        self, stage: PipelineStage, task_func: Callable[[], Any]
    ) -> Any:
        attempts = 0
        last_exception = None

        while attempts < (self.max_attempts if self.enabled else 1):
            attempts += 1
            try:
                return task_func()
            except Exception as e:
                last_exception = e
                if not self.is_retryable(stage, e) or attempts >= self.max_attempts:
                    raise e
                time.sleep(self.backoff_seconds * attempts)

        if last_exception:
            raise last_exception
