"""
Unit and Integration Test Suite for End-to-End Research Orchestration OS (Phase 29).
"""

import pytest
from fastapi.testclient import TestClient

from orchestration.dependency_graph import PipelineDependencyGraph
from orchestration.stage_registry import StageRegistry
from orchestration.pipeline import ResearchPipelineEngine
from orchestration.pipeline_context import PipelineContext
from orchestration.validation import PipelineValidationGates
from orchestration.checkpoints import CheckpointManager
from orchestration.recovery import RecoveryEngine
from orchestration.lineage import LineageTracer
from orchestration.reports.generator import ResearchReportGenerator
from orchestration.services.orchestration_service import OrchestrationService
from api.main import app


def test_dependency_graph_order():
    graph = PipelineDependencyGraph()
    order = graph.get_execution_order()

    assert len(order) == 14
    assert order[0] == "DATA"
    assert order[-1] == "REPORT"
    assert order.index("DATA") < order.index("FEATURES")
    assert order.index("FEATURES") < order.index("VALIDATION")
    assert order.index("VALIDATION") < order.index("TRAINING")
    assert order.index("TRAINING") < order.index("PREDICTION")
    assert order.index("PREDICTION") < order.index("ALPHA")
    assert order.index("ALPHA") < order.index("PORTFOLIO")
    assert order.index("PORTFOLIO") < order.index("EXECUTION")
    assert order.index("EXECUTION") < order.index("BACKTEST")
    assert order.index("BACKTEST") < order.index("RISK")
    assert order.index("RISK") < order.index("STATISTICS")
    assert order.index("STATISTICS") < order.index("ROBUSTNESS")
    assert order.index("ROBUSTNESS") < order.index("MONITORING")
    assert order.index("MONITORING") < order.index("REPORT")


def test_stage_registry_all_stages():
    registry = StageRegistry()
    stages = registry.list_stages()

    assert len(stages) == 14
    for name in stages:
        stage = registry.get_stage(name)
        assert stage.name == name


def test_full_14_stage_pipeline_execution():
    engine = ResearchPipelineEngine()
    state = engine.run_pipeline(
        experiment_id="EXP-FULL-TEST",
        symbols=["AAPL", "MSFT"],
        config={"strict_leakage": False},
    )

    assert state.status == "COMPLETED"
    assert len(state.completed_stages) == 14
    assert state.duration_seconds > 0.0


def test_checkpoints_and_recovery():
    chk_mgr = CheckpointManager()
    engine = ResearchPipelineEngine()
    state = engine.run_pipeline("EXP-RECOVERY-TEST", config={"strict_leakage": False})

    chk_path = chk_mgr.save_checkpoint(state)
    assert chk_path is not None

    loaded = chk_mgr.load_checkpoint(state.run_id)
    assert loaded is not None
    assert loaded.run_id == state.run_id

    recovery = RecoveryEngine(chk_mgr)
    all_stages = PipelineDependencyGraph().get_execution_order()
    resume_stages = recovery.get_resume_stages(state.run_id, all_stages)
    assert len(resume_stages) == 0  # All completed


def test_lineage_tracer_and_report_generator():
    context = PipelineContext(experiment_id="EXP-REP-TEST", run_id="RUN-REP-TEST")
    tracer = LineageTracer()
    lineage = tracer.trace_lineage(context)

    assert lineage.experiment_id == "EXP-REP-TEST"
    assert lineage.model_id.startswith("MODEL-")

    generator = ResearchReportGenerator()
    report_md = generator.generate_research_report(context)

    assert "# Multi-Modal Quant AI — Institutional Research Report" in report_md
    assert "Executive Summary" in report_md


def test_orchestration_service_and_api():
    client = TestClient(app)

    # Test GET health
    h_res = client.get("/pipeline/health")
    assert h_res.status_code == 200
    assert h_res.json()["status"] == "healthy"

    # Test POST run
    r_res = client.post(
        "/pipeline/run",
        json={"experiment_id": "EXP-API-PIPE", "symbols": ["AAPL"]},
    )
    assert r_res.status_code == 200
    data = r_res.json()
    assert data["status"] == "COMPLETED"
    assert len(data["completed_stages"]) == 14
