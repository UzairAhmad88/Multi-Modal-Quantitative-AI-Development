"""
Unit & Integration Tests for Research Pipeline Orchestration Engine.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from orchestration.dependency_graph import PipelineDependencyGraph
from orchestration.stage_registry import StageRegistry
from orchestration.pipeline import ResearchPipelineEngine
from orchestration.pipeline_context import PipelineContext
from orchestration.pipeline_state import PipelineRunState, PipelineStatus
from orchestration.checkpoints import CheckpointManager


def test_dependency_graph_ordered_stages():
    graph = PipelineDependencyGraph()
    stages = graph.get_execution_order()
    assert len(stages) == 14
    assert stages[0] == "DATA"
    assert stages[-1] == "REPORT"
    assert graph.get_prerequisites("FEATURES") == ["DATA"]


def test_stage_registry():
    registry = StageRegistry()
    stages = registry.list_stages()
    assert len(stages) == 14
    assert "DATA" in stages
    assert "REPORT" in stages


def test_research_pipeline_execution():
    engine = ResearchPipelineEngine()
    state = engine.run_pipeline(
        experiment_id="EXP-UNIT-TEST",
        symbols=["AAPL"],
        config={"strict_leakage": False}
    )
    assert state.status == PipelineStatus.COMPLETED
    assert len(state.completed_stages) == 14
    assert state.duration_seconds > 0.0


def test_checkpoint_manager():
    with tempfile.TemporaryDirectory() as temp_dir:
        chk_mgr = CheckpointManager(checkpoints_dir=temp_dir)
        state = PipelineRunState(
            run_id="RUN-TEST-001",
            experiment_id="EXP-TEST-001",
            status=PipelineStatus.RUNNING,
            completed_stages=["DATA", "FEATURES"]
        )
        saved_path = chk_mgr.save_checkpoint(state)
        assert saved_path is not None

        loaded = chk_mgr.load_checkpoint("RUN-TEST-001")
        assert loaded is not None
        assert loaded.run_id == "RUN-TEST-001"
        assert loaded.completed_stages == ["DATA", "FEATURES"]
