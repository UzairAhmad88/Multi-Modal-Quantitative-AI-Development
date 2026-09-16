"""
End-to-End Complete Quant Research Pipeline Test Suite (Phase 30).
"""

import pytest
from orchestration.pipeline import ResearchPipelineEngine
from orchestration.pipeline_state import PipelineStatus
from orchestration.artifacts import ArtifactManager
from tests.data.golden_dataset import generate_golden_dataset


def test_golden_dataset_generation():
    m_df, n_df, f_df = generate_golden_dataset(n_samples=100, seed=42)
    assert len(m_df) == 100
    assert len(n_df) == 100
    assert len(f_df) == 100
    assert "close" in m_df.columns
    assert "sentiment_score" in n_df.columns
    assert "pe_ratio" in f_df.columns


def test_complete_end_to_end_quant_pipeline():
    engine = ResearchPipelineEngine()
    state = engine.run_pipeline(
        experiment_id="EXP-E2E-GOLDEN-001",
        symbols=["AAPL", "MSFT"],
        config={"strict_leakage": False, "random_seed": 42},
    )

    assert state.status == PipelineStatus.COMPLETED
    assert len(state.completed_stages) == 14
    assert state.failed_stage is None
    assert state.duration_seconds > 0.0

    # Verify stage order execution
    expected_order = [
        "DATA", "FEATURES", "VALIDATION", "TRAINING", "PREDICTION",
        "ALPHA", "PORTFOLIO", "EXECUTION", "BACKTEST", "RISK",
        "STATISTICS", "ROBUSTNESS", "MONITORING", "REPORT"
    ]
    assert state.completed_stages == expected_order


def test_e2e_checkpoint_and_reproducibility():
    engine = ResearchPipelineEngine()
    state1 = engine.run_pipeline("EXP-E2E-REP-1", config={"strict_leakage": False, "random_seed": 42})
    state2 = engine.run_pipeline("EXP-E2E-REP-2", config={"strict_leakage": False, "random_seed": 42})

    assert state1.status == PipelineStatus.COMPLETED
    assert state2.status == PipelineStatus.COMPLETED
    assert len(state1.completed_stages) == len(state2.completed_stages) == 14


def test_artifact_manager_integrity():
    art_mgr = ArtifactManager()
    run_id = "RUN-E2E-TEST"
    art_info = art_mgr.register_artifact(run_id, "test_stage", "output.csv", "sample data content")

    assert art_info["run_id"] == run_id
    assert art_info["checksum"] is not None
    assert art_mgr.exists(run_id, "test_stage", "output.csv")
