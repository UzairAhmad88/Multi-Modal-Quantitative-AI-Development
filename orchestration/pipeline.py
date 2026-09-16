"""
Master Research Pipeline Orchestrator for Multi-Modal Quant AI.
Orchestrates all 17 stages, enforces DAG dependencies, checkpoint resumes, resource limits, and artifact registration.
"""

from typing import Dict, List, Any, Optional
import time
import datetime
import uuid
from orchestration.dependency_graph import DependencyGraph, PipelineStage
from orchestration.state_manager import StateManager, PipelineState, StageState
from orchestration.checkpoint_manager import CheckpointManager
from orchestration.retry_manager import RetryManager
from orchestration.resource_manager import ResourceManager
from orchestration.artifact_manager import ArtifactManager
from orchestration.logging_manager import LoggingManager
from orchestration.task_registry import TaskRegistry
from orchestration.executor import StageExecutor
from research.registry.registry import ExperimentRegistry


class ResearchPipeline:
    """Master 17-stage DAG pipeline orchestrator."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        resume_run_id: Optional[str] = None,
        artifact_dir: str = "artifacts",
        log_dir: str = "logs/runs",
        max_memory_gb: float = 8.0,
        max_runtime_minutes: float = 120.0,
    ):
        self.config = config or {}
        self.resume_run_id = resume_run_id
        self.artifact_dir = artifact_dir
        self.log_dir = log_dir
        self.state_manager = StateManager()
        self.checkpoint_manager = CheckpointManager(artifact_dir)
        self.retry_manager = RetryManager(enabled=True, max_attempts=3)
        self.resource_manager = ResourceManager(max_memory_gb=max_memory_gb, max_runtime_minutes=max_runtime_minutes)
        self.artifact_manager = ArtifactManager(artifact_dir)
        self.logging_manager = LoggingManager(log_dir)
        self.task_registry = TaskRegistry()
        self.executor = StageExecutor(self.checkpoint_manager, self.retry_manager, self.resource_manager)
        self.registry = ExperimentRegistry()

        self.experiment_id = f"EXP-{self._generate_timestamp_id()}"
        self.run_id = self.resume_run_id or f"RUN-{self._generate_timestamp_id()}"

    @staticmethod
    def _generate_timestamp_id() -> str:
        now = datetime.datetime.utcnow()
        return f"{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

    def execute(self) -> Dict[str, Any]:
        """Convenience method to execute current pipeline instance."""
        return self.execute_pipeline(
            experiment_id=self.experiment_id,
            config=self.config,
            run_id=self.run_id,
            resume_run_id=self.resume_run_id
        )

    def execute_pipeline(
        self,
        experiment_id: str,
        config: Dict[str, Any],
        run_id: Optional[str] = None,
        resume_run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Executes full 17-stage research pipeline with DAG validation and checkpoint resume support."""
        actual_run_id = run_id or resume_run_id or f"RUN-{self._generate_timestamp_id()}"

        run_state = self.state_manager.get_run_state(actual_run_id)
        if not run_state:
            run_state = self.state_manager.create_run_state(actual_run_id, experiment_id, metadata={"config": config})

        self.state_manager.start_pipeline(actual_run_id)
        self.logging_manager.log_event(actual_run_id, "PIPELINE", "STARTED", message=f"Pipeline run {actual_run_id} started for experiment {experiment_id}")

        self.registry.register_experiment(experiment_id, config.get("experiment", {}).get("name", "experiment"), config)
        self.registry.register_run(actual_run_id, experiment_id, config, status="RUNNING")

        start_time = time.time()
        ctx: Dict[str, Any] = {"experiment_id": experiment_id, "run_id": actual_run_id, "config": config}
        completed_stages = set()

        ordered_stages = DependencyGraph.get_ordered_stages()

        for stage in ordered_stages:
            stage_name = stage.value

            # Failure injection for testing
            if config.get("_inject_failure_stage") == stage_name:
                err_msg = f"Injected failure in stage {stage_name}"
                self.state_manager.fail_stage(actual_run_id, stage, err_msg)
                self.logging_manager.log_event(actual_run_id, stage_name, "FAILED", severity="ERROR", message=err_msg)
                self.registry.update_run_status(actual_run_id, status="FAILED", error=err_msg)
                return {
                    "status": "FAILED",
                    "failed_stage": stage_name,
                    "experiment_id": experiment_id,
                    "run_id": actual_run_id,
                    "error": err_msg,
                    "completed_stages": len(completed_stages),
                    "total_stages": len(ordered_stages),
                }

            # Check if resuming from checkpoint
            if resume_run_id and self.checkpoint_manager.has_checkpoint(experiment_id, stage):
                checkpoint_data = self.checkpoint_manager.load_checkpoint(experiment_id, stage)
                if checkpoint_data:
                    ctx[stage_name] = checkpoint_data
                    completed_stages.add(stage)
                    self.state_manager.start_stage(actual_run_id, stage)
                    self.state_manager.complete_stage(actual_run_id, stage, duration=0.0)
                    self.logging_manager.log_event(actual_run_id, stage_name, "SKIPPED", message=f"Loaded stage {stage_name} from checkpoint")
                    continue

            # Ensure dependencies are met
            if not DependencyGraph.is_stage_ready(stage, completed_stages):
                err_msg = f"Prerequisites for stage {stage_name} not satisfied."
                self.state_manager.fail_stage(actual_run_id, stage, err_msg)
                self.logging_manager.log_event(actual_run_id, stage_name, "FAILED", severity="ERROR", message=err_msg)
                self.registry.update_run_status(actual_run_id, status="FAILED", error=err_msg)
                raise RuntimeError(err_msg)

            # Execute stage
            self.state_manager.start_stage(actual_run_id, stage)
            self.logging_manager.log_event(actual_run_id, stage_name, "RUNNING")

            try:
                handler = self.task_registry.get_handler(stage)
                seed = config.get("experiment", {}).get("seed", 42)
                stage_result = self.executor.execute_stage(experiment_id, stage, handler, ctx, seed=seed)

                ctx[stage_name] = stage_result
                completed_stages.add(stage)
                duration = stage_result.get("_duration_seconds", 0.0)
                self.state_manager.complete_stage(actual_run_id, stage, duration=duration)
                self.logging_manager.log_event(actual_run_id, stage_name, "COMPLETED", message=f"Stage {stage_name} completed in {duration:.2f}s")

            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                self.state_manager.fail_stage(actual_run_id, stage, str(e), stack_trace=tb)
                self.logging_manager.log_event(actual_run_id, stage_name, "FAILED", severity="ERROR", message=str(e), extra={"stack_trace": tb})
                self.registry.update_run_status(actual_run_id, status="FAILED", error=str(e))
                return {
                    "status": "FAILED",
                    "failed_stage": stage_name,
                    "experiment_id": experiment_id,
                    "run_id": actual_run_id,
                    "error": str(e),
                    "completed_stages": len(completed_stages),
                    "total_stages": len(ordered_stages),
                }

        total_duration = time.time() - start_time
        self.state_manager.complete_pipeline(actual_run_id, duration=total_duration)

        # Register artifact manifest
        manifest_path = self.artifact_manager.register_artifact_manifest(
            experiment_id=experiment_id,
            run_id=actual_run_id,
            dataset=ctx.get("DATA", {}).get("dataset_id", "DS-SP500"),
            features=config.get("features", []),
            model=config.get("model", {}).get("type", "multimodal"),
            backtest=ctx.get("BACKTEST", {}),
            validation=ctx.get("VALIDATION", {}),
            report_path=ctx.get("REPORT", {}).get("report_path", f"reports/experiments/{experiment_id}_report.md"),
        )

        metrics = ctx.get("BACKTEST", {})
        artifacts = {"manifest": manifest_path}

        self.registry.update_run_status(actual_run_id, status="COMPLETED", metrics=metrics, artifacts=artifacts)

        return {
            "status": "COMPLETED",
            "experiment_id": experiment_id,
            "run_id": actual_run_id,
            "completed_stages": len(completed_stages),
            "total_stages": len(ordered_stages),
            "total_duration_seconds": round(total_duration, 2),
            "manifest_path": manifest_path,
            "metrics": metrics,
            "results": ctx,
        }
