"""
Stage Executor for Pipeline Task Invocation.
Enforces seed initialization, timing, resource constraint checks, retries, and stage checkpointing.
"""

from typing import Dict, Any, Callable
import time
import random
import numpy as np
from orchestration.dependency_graph import PipelineStage
from orchestration.retry_manager import RetryManager
from orchestration.resource_manager import ResourceManager
from orchestration.checkpoint_manager import CheckpointManager


class StageExecutor:
    """Executes single pipeline stage tasks under resource and seed management."""

    def __init__(
        self,
        checkpoint_manager: CheckpointManager,
        retry_manager: RetryManager,
        resource_manager: ResourceManager,
    ):
        self.checkpoint_manager = checkpoint_manager
        self.retry_manager = retry_manager
        self.resource_manager = resource_manager

    def set_random_seeds(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        try:
            import torch
            torch.manual_seed(seed)
        except ImportError:
            pass

    def execute_stage(
        self,
        experiment_id: str,
        stage: PipelineStage,
        task_func: Callable[[Dict[str, Any]], Dict[str, Any]],
        ctx: Dict[str, Any],
        seed: int = 42,
    ) -> Dict[str, Any]:
        self.set_random_seeds(seed)
        self.resource_manager.check_limits()

        start_time = time.time()

        def _run():
            return task_func(ctx)

        result_data = self.retry_manager.execute_with_retry(stage, _run)
        duration = time.time() - start_time

        # Save checkpoint
        checkpoint_path = self.checkpoint_manager.save_checkpoint(experiment_id, stage, result_data)
        result_data["_duration_seconds"] = duration
        result_data["_checkpoint_path"] = checkpoint_path

        return result_data
