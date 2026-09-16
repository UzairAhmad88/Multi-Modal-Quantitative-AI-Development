"""
Master Unified Pipeline Orchestrator Engine for End-to-End Research OS.
"""

import datetime
import time
import uuid
from typing import Any, Dict, List, Optional
from .pipeline_context import PipelineContext
from .pipeline_state import PipelineRunState, PipelineStatus, StageStatus, StageState
from .stage_registry import StageRegistry
from .dependency_graph import PipelineDependencyGraph
from .validation import PipelineValidationGates
from .checkpoints import CheckpointManager
from .recovery import RecoveryEngine
from .events import EventEmitter, PipelineEventType


class ResearchPipelineEngine:
    """Master Unified End-to-End Quantitative Research Pipeline Engine."""


    def __init__(self, checkpoints_dir: Optional[str] = None):
        self.stage_registry = StageRegistry()
        self.dependency_graph = PipelineDependencyGraph()
        self.checkpoint_mgr = CheckpointManager(checkpoints_dir)
        self.recovery_engine = RecoveryEngine(self.checkpoint_mgr)
        self.event_emitter = EventEmitter()

    def run_pipeline(
        self,
        experiment_id: str = "EXP-END2END-001",
        config: Optional[Dict[str, Any]] = None,
        symbols: Optional[List[str]] = None,
        resume_run_id: Optional[str] = None,
        start_stage: Optional[str] = None,
        end_stage: Optional[str] = None,
    ) -> PipelineRunState:
        run_id = resume_run_id or f"RUN-{uuid.uuid4().hex[:8].upper()}"
        config = config or {}
        symbols = symbols or ["AAPL", "MSFT"]

        context = PipelineContext(
            experiment_id=experiment_id,
            run_id=run_id,
            symbols=symbols,
            config=config,
            random_seed=config.get("random_seed", 42),
        )

        all_stages = self.dependency_graph.get_execution_order()

        # Handle stage subset selection if requested
        if start_stage or end_stage:
            start_idx = all_stages.index(start_stage) if start_stage in all_stages else 0
            end_idx = all_stages.index(end_stage) + 1 if end_stage in all_stages else len(all_stages)
            stages_to_run = all_stages[start_idx:end_idx]
        elif resume_run_id:
            stages_to_run = self.recovery_engine.get_resume_stages(resume_run_id, all_stages)
        else:
            stages_to_run = list(all_stages)

        run_state = PipelineRunState(
            run_id=run_id,
            experiment_id=experiment_id,
            status=PipelineStatus.RUNNING,
            started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

        self.event_emitter.emit(
            event_id=f"EVT-{uuid.uuid4().hex[:6]}",
            run_id=run_id,
            experiment_id=experiment_id,
            event_type=PipelineEventType.PIPELINE_STARTED,
            message=f"Starting end-to-end research pipeline for experiment '{experiment_id}'",
        )

        start_t = time.time()

        for stage_name in all_stages:
            if stage_name not in stages_to_run:
                # Keep completed status if resuming
                if stage_name in run_state.completed_stages:
                    continue

            run_state.current_stage = stage_name
            self.event_emitter.emit(
                event_id=f"EVT-{uuid.uuid4().hex[:6]}",
                run_id=run_id,
                experiment_id=experiment_id,
                event_type=PipelineEventType.STAGE_STARTED,
                stage_name=stage_name,
                message=f"Executing pipeline stage '{stage_name}'",
            )

            stage_handler = self.stage_registry.get_stage(stage_name)
            st_state = stage_handler.run_stage(context)
            run_state.stages[stage_name] = st_state

            if st_state.status == StageStatus.COMPLETED:
                run_state.completed_stages.append(stage_name)
                self.event_emitter.emit(
                    event_id=f"EVT-{uuid.uuid4().hex[:6]}",
                    run_id=run_id,
                    experiment_id=experiment_id,
                    event_type=PipelineEventType.STAGE_COMPLETED,
                    stage_name=stage_name,
                    message=f"Completed stage '{stage_name}' in {st_state.duration_seconds:.2f}s",
                )
                # Audit gates
                if stage_name == "DATA":
                    PipelineValidationGates.audit_data_gate(context)
                elif stage_name == "VALIDATION":
                    PipelineValidationGates.audit_leakage_gate(context)
                elif stage_name == "RISK":
                    PipelineValidationGates.audit_risk_gate(context)
                elif stage_name == "MONITORING":
                    PipelineValidationGates.audit_monitoring_gate(context)

                # Persist stage checkpoint
                self.checkpoint_mgr.save_checkpoint(run_state)

            else:
                run_state.status = PipelineStatus.FAILED
                run_state.failed_stage = stage_name
                run_state.completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                run_state.duration_seconds = round(time.time() - start_t, 4)

                self.event_emitter.emit(
                    event_id=f"EVT-{uuid.uuid4().hex[:6]}",
                    run_id=run_id,
                    experiment_id=experiment_id,
                    event_type=PipelineEventType.STAGE_FAILED,
                    stage_name=stage_name,
                    message=f"Pipeline stage '{stage_name}' failed: {st_state.error_message}",
                )
                self.checkpoint_mgr.save_checkpoint(run_state)
                return run_state

        run_state.status = PipelineStatus.COMPLETED
        run_state.completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        run_state.duration_seconds = round(time.time() - start_t, 4)
        run_state.current_stage = None

        self.checkpoint_mgr.save_checkpoint(run_state)

        self.event_emitter.emit(
            event_id=f"EVT-{uuid.uuid4().hex[:6]}",
            run_id=run_id,
            experiment_id=experiment_id,
            event_type=PipelineEventType.PIPELINE_COMPLETED,
            message=f"Completed full 14-stage research pipeline run '{run_id}' in {run_state.duration_seconds:.2f}s",
        )

        return run_state


# Alias for backward compatibility with Phase 14
ResearchPipeline = ResearchPipelineEngine

