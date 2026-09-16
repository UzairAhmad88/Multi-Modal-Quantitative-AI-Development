"""
Abstract Base Class for Pipeline Stages in End-to-End Orchestration OS.
"""

from abc import ABC, abstractmethod
import time
from typing import Any, Dict
from .pipeline_context import PipelineContext
from .pipeline_state import StageState, StageStatus


class PipelineStage(ABC):
    """Abstract base class for all 14 quantitative pipeline stages."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def validate(self, context: PipelineContext) -> bool:
        """Validates prerequisites and inputs before execution."""
        pass

    @abstractmethod
    def execute(self, context: PipelineContext) -> Dict[str, Any]:
        """Executes the stage logic and returns stage artifacts/outputs."""
        pass

    def run_stage(self, context: PipelineContext) -> StageState:
        """Runs the stage lifecycle: validate -> execute -> update context."""
        state = StageState(stage_name=self.name, status=StageStatus.RUNNING)
        start_t = time.time()

        try:
            if not self.validate(context):
                state.status = StageStatus.FAILED
                state.error_message = f"Validation failed for stage '{self.name}'"
                return state

            outputs = self.execute(context)
            context.stage_data[self.name] = outputs

            state.status = StageStatus.COMPLETED
            state.duration_seconds = round(time.time() - start_t, 4)
            if isinstance(outputs, dict) and "artifacts" in outputs:
                state.artifacts = outputs["artifacts"]
                context.artifacts.update(outputs["artifacts"])

        except Exception as e:
            state.status = StageStatus.FAILED
            state.error_message = str(e)
            state.duration_seconds = round(time.time() - start_t, 4)
            context.errors.append(f"Stage '{self.name}' failed: {str(e)}")

        return state
