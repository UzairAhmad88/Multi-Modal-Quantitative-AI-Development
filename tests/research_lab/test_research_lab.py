"""
Unit & Integration Tests for Phase 21 Systematic Research Laboratory OS.
"""

import pytest
from research_lab.experiments.states import ExperimentStatus, RunStatus
from research_lab.schemas.experiment_schema import Experiment
from research_lab.hypotheses.hypothesis_manager import HypothesisManager
from research_lab.runs.experiment_run import ExperimentRun
from research_lab.tracking.metric_store import MetricStore
from research_lab.artifacts.artifact_store import ArtifactStore
from research_lab.lineage.lineage_graph import LineageGraph
from research_lab.comparison.comparison_engine import ExperimentComparisonEngine
from research_lab.comparison.experiment_diff import ExperimentDiff
from research_lab.knowledge_base.knowledge_base import ResearchKnowledgeBase, Finding
from research_lab.intelligence.research_intelligence_engine import ResearchIntelligenceEngine
from research_lab.reproducibility.reproducibility_checker import ReproducibilityChecker
from research_lab.experiments.templates import get_template
from research_lab.manager import ExperimentManager


def test_experiment_schema_and_hash():
    exp = Experiment(
        experiment_id="EXP-TEST-001",
        name="Test Experiment",
        description="Testing schema",
        hypothesis={"q": "Question?"},
        dataset_id="DS-TEST",
        feature_version="v1.0.0",
        model_version="xgboost_alpha",
        strategy_id="TEST_ALPHA",
        portfolio_config={"method": "mean_variance"},
        execution_config={"algorithm": "MARKET"},
        evaluation_config={"walk_forward": True}
    )
    h1 = exp.compute_config_hash()
    assert len(h1) == 16
    assert exp.status == ExperimentStatus.DRAFT

    # Re-computing hash on identical fields must yield identical hash
    h2 = exp.compute_config_hash()
    assert h1 == h2


def test_hypothesis_manager():
    mgr = HypothesisManager()
    h = mgr.create_hypothesis(
        question="Does sentiment help?",
        hypothesis="Sentiment improves Sharpe",
        expected_behavior="Sharpe increases from 1.0 to 1.4",
        null_hypothesis="No change in Sharpe",
        success_criteria="Sharpe >= 1.2"
    )
    assert h.research_question == "Does sentiment help?"
    assert h.null_hypothesis == "No change in Sharpe"


def test_experiment_run_lifecycle():
    run = ExperimentRun(experiment_id="EXP-001")
    assert run.status == RunStatus.QUEUED

    run.complete_run(metrics={"sharpe": 1.5}, artifacts={"report": "report.md"})
    assert run.status == RunStatus.COMPLETED
    assert run.metrics["sharpe"] == 1.5


def test_lineage_graph():
    graph = LineageGraph()
    res = graph.build_lineage(
        experiment_id="EXP-001",
        dataset_id="DS-001",
        feature_version="v1",
        model_version="v1",
        strategy_id="S1",
        portfolio_id="P1",
        execution_id="E1",
        backtest_id="B1",
        evaluation_id="EV1",
        report_id="R1"
    )
    assert res["depth"] == 10
    assert res["lineage_dag"][0]["node"] == "Dataset"
    assert res["lineage_dag"][-1]["node"] == "Report"


def test_comparison_and_diff():
    comp = ExperimentComparisonEngine()
    diff = ExperimentDiff()

    e1 = {"experiment_id": "EXP-1", "dataset_id": "DS-A", "metrics": {"sharpe_ratio": 1.5}}
    e2 = {"experiment_id": "EXP-2", "dataset_id": "DS-B", "metrics": {"sharpe_ratio": 1.2}}

    comp_res = comp.compare_experiments([e1, e2])
    assert comp_res["is_fair_comparison"] is False
    assert len(comp_res["comparability_warnings"]) == 1

    diff_res = diff.diff_experiments(e1, e2)
    assert diff_res["has_differences"] is True
    assert "dataset_id" in diff_res["configuration_diffs"]


def test_knowledge_base_and_intelligence():
    kb = ResearchKnowledgeBase()
    kb.add_finding(Finding(experiment_id="EXP-001", statement="Multimodal fusion improves Sharpe ratio"))
    kb.add_note(experiment_id="EXP-001", note_text="Observed strong performance under low vol")

    search_res = kb.search_knowledge("multimodal")
    assert len(search_res) == 1
    assert search_res[0]["type"] == "FINDING"

    intel = ResearchIntelligenceEngine()
    syn = intel.synthesize_insights([{"experiment_id": "EXP-001", "name": "Test", "metrics": {"sharpe_ratio": 1.5}}])
    assert syn["insights_count"] > 0


def test_reproducibility_checker():
    checker = ReproducibilityChecker()
    exp_a = {"configuration_hash": "HASH123", "random_seed": 42, "metrics": {"sharpe_ratio": 1.500}}
    exp_b = {"configuration_hash": "HASH123", "random_seed": 42, "metrics": {"sharpe_ratio": 1.500}}

    status, details = checker.verify_reproducibility(exp_a, exp_b)
    assert status == "MATCH"
    assert details["seed_match"] is True


def test_experiment_manager_pipeline():
    mgr = ExperimentManager()
    exp = mgr.create_experiment(name="Pipeline Test", template_name="multimodal")

    assert exp.status == ExperimentStatus.READY
    assert len(exp.configuration_hash) == 16

    res = mgr.run_experiment(exp.experiment_id)
    assert res["status"] == ExperimentStatus.COMPLETED.value
    assert "metrics" in res
    assert "lineage" in res
    assert "reports" in res

    rep_res = mgr.replicate_experiment(exp.experiment_id)
    assert rep_res["reproducibility_status"] in ("MATCH", "PARTIAL_MATCH")
