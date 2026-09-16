"""
Comprehensive Unit and Integration Test Suite for Research Intelligence (Phase 11).
Tests Hypothesis Management, Experiment Runner, Priority Queue, Deduplication, Comparison Engine,
Ablation, Robustness, Diagnostics, Memory Lineage, Claim Validation, Recommender, and Reports.
"""

import pytest
from typing import Dict, Any
from research_intelligence.hypothesis.registry import (
    HypothesisRegistry,
    HypothesisState,
    PreRegistrationSpec,
)
from research_intelligence.experiment_manager.manager import (
    IntelExperimentManager,
    ExperimentConfig,
    ExperimentPriority,
    ExperimentStatus,
)
from research_intelligence.experiment_runner.runner import IntelExperimentRunner
from research_intelligence.experiment_generator.generator import (
    ExperimentGenerator,
    SearchSpace,
    ResearchBatchRunner,
)
from research_intelligence.comparison.comparator import ExperimentComparator
from research_intelligence.ablation.intel_ablation import IntelAblationEngine
from research_intelligence.robustness.intel_robustness import IntelRobustnessEngine
from research_intelligence.diagnostics.error_analyzer import (
    ErrorAnalyzer,
    ConfidenceCalibrator,
    ExplainabilityEngine,
)
from research_intelligence.research_memory.memory import (
    ResearchMemory,
    ResearchFinding,
    ResearchClaimValidator,
)
from research_intelligence.recommendation_engine.recommender import ResearchRecommendationEngine
from research_intelligence.report_generator.generator import ResearchReportGenerator
from research_intelligence.orchestration.pipeline import ResearchIntelligencePipeline


def test_hypothesis_registration_and_preregistration():
    registry = HypothesisRegistry()
    prereg = PreRegistrationSpec(
        objective="Test VIX regime filter",
        dataset="market_sp500",
        features=["market_return", "vix"],
        model="LSTM",
        evaluation_metrics=["sharpe"],
        period="2021-2026",
        expected_relationship="Lower drawdown",
    )
    hypo = registry.register(
        title="VIX Regime Filter",
        description="Filter out high vix regimes",
        research_question="Does VIX filtering lower drawdown?",
        expected_effect="Lower drawdown",
        null_hypothesis="No effect",
        variables=["market_return", "vix"],
        dataset="market_sp500",
        time_period="2021-2026",
        preregistration=prereg,
    )
    assert hypo.hypothesis_id.startswith("HYP-")
    assert hypo.status == HypothesisState.REGISTERED
    assert hypo.preregistration is not None

    # Test state update
    updated = registry.update_status(hypo.hypothesis_id, HypothesisState.SUPPORTED)
    assert updated.status == HypothesisState.SUPPORTED


def test_experiment_manager_priority_and_approval():
    manager = IntelExperimentManager()
    cfg1 = ExperimentConfig(
        name="Exp_Low", hypothesis_id="HYP-1", dataset="sp500", features=["ret"], model="LSTM"
    )
    cfg2 = ExperimentConfig(
        name="Exp_High", hypothesis_id="HYP-1", dataset="sp500", features=["ret"], model="LSTM"
    )

    rec1 = manager.create_experiment(cfg1, priority=ExperimentPriority.LOW, auto_approve=True)
    rec2 = manager.create_experiment(cfg2, priority=ExperimentPriority.HIGH, auto_approve=True)

    queued = manager.get_queued_experiments()
    assert len(queued) == 2
    assert queued[0].experiment_id == rec2.experiment_id  # HIGH priority first


def test_experiment_approval_enforcement():
    manager = IntelExperimentManager()
    runner = IntelExperimentRunner(manager)
    cfg = ExperimentConfig(
        name="Exp_Unapproved", hypothesis_id="HYP-1", dataset="sp500", features=["ret"], model="LSTM"
    )
    rec = manager.create_experiment(cfg, auto_approve=False)

    with pytest.raises(PermissionError):
        runner.run_experiment(rec.experiment_id)

    manager.approve_experiment(rec.experiment_id)
    res = runner.run_experiment(rec.experiment_id)
    assert res["trading_metrics"]["sharpe"] > 0


def test_experiment_deduplication():
    manager = IntelExperimentManager()
    memory = ResearchMemory()
    runner = IntelExperimentRunner(manager, memory)

    cfg = ExperimentConfig(
        name="Exp_Dedup", hypothesis_id="HYP-1", dataset="sp500", features=["ret"], model="LSTM"
    )
    rec1 = manager.create_experiment(cfg, auto_approve=True)
    res1 = runner.run_experiment(rec1.experiment_id)

    rec2 = manager.create_experiment(cfg, auto_approve=True)
    res2 = runner.run_experiment(rec2.experiment_id)

    assert res2.get("reused_from") == rec1.experiment_id


def test_experiment_comparator():
    manager = IntelExperimentManager()
    runner = IntelExperimentRunner(manager)

    cfg1 = ExperimentConfig(
        name="Exp_A", hypothesis_id="HYP-1", dataset="sp500", features=["ret"], model="LSTM"
    )
    cfg2 = ExperimentConfig(
        name="Exp_B", hypothesis_id="HYP-1", dataset="sp500", features=["ret", "news"], model="LSTM"
    )

    rec1 = manager.create_experiment(cfg1, auto_approve=True)
    rec2 = manager.create_experiment(cfg2, auto_approve=True)

    runner.run_experiment(rec1.experiment_id)
    runner.run_experiment(rec2.experiment_id)

    comp = ExperimentComparator.compare(rec1, rec2)
    assert comp["configuration_diff"]["added_features"] == ["news"]
    assert "metrics_comparison" in comp


def test_ablation_engine():
    manager = IntelExperimentManager()
    runner = IntelExperimentRunner(manager)
    ablation = IntelAblationEngine(manager, runner)

    cfg = ExperimentConfig(
        name="Exp_Ablation_Base",
        hypothesis_id="HYP-1",
        dataset="sp500",
        features=["market_return", "news_sentiment", "pe_ratio"],
        model="Transformer",
    )
    res = ablation.run_ablation_study(cfg, "HYP-1")
    assert "FULL" in res["modality_results"]
    assert "FULL_MINUS_NEWS" in res["modality_results"]


def test_robustness_engine():
    manager = IntelExperimentManager()
    runner = IntelExperimentRunner(manager)
    robustness = IntelRobustnessEngine(manager, runner)

    cfg = ExperimentConfig(
        name="Exp_Robustness_Base",
        hypothesis_id="HYP-1",
        dataset="sp500",
        features=["market_return"],
        model="GRU",
    )
    res = robustness.run_robustness_suite(cfg, "HYP-1")
    assert "cost_sensitivity" in res
    assert "stability_score" in res


def test_confidence_calibrator_and_diagnostics():
    calibrator = ConfidenceCalibrator()
    res = calibrator.evaluate_calibration([0.9, 0.8, 0.7, 0.6], [True, True, False, True])
    assert "expected_calibration_error" in res

    analyzer = ErrorAnalyzer()
    out = analyzer.analyze_experiment_errors("EXP-1", ["market_return"])
    assert out["directional_error_rate"] >= 0.0


def test_prohibited_claim_validator():
    # Prohibited claims must raise ValueError
    with pytest.raises(ValueError):
        ResearchClaimValidator.validate_statement("This model provides a guaranteed return of 50%.")

    with pytest.raises(ValueError):
        ResearchClaimValidator.validate_statement("Strategy is 100% risk-free.")

    # Valid non-promotional claim passes
    assert ResearchClaimValidator.validate_statement("An observed Sharpe ratio of 1.72 was measured.") is True


def test_research_memory_and_lineage():
    memory = ResearchMemory()
    manager = IntelExperimentManager()
    cfg = ExperimentConfig(
        name="Exp_Lineage", hypothesis_id="HYP-100", dataset="sp500", features=["ret"], model="LSTM"
    )
    rec = manager.create_experiment(cfg, auto_approve=True)
    memory.store_experiment(rec)

    fnd = memory.store_finding(
        experiment_id=rec.experiment_id,
        statement="Observed baseline Sharpe ratio of 1.5.",
        evidence="Backtest metrics",
        metrics={"sharpe": 1.5},
        period="2021-2026",
        confidence=0.9,
        limitations="Simulated paper-trading",
    )
    assert fnd.finding_id.startswith("FND-")

    lineage = memory.get_lineage(rec.experiment_id)
    assert lineage["hypothesis_id"] == "HYP-100"
    assert len(lineage["findings"]) == 1


def test_recommendation_engine():
    manager = IntelExperimentManager()
    runner = IntelExperimentRunner(manager)
    cfg = ExperimentConfig(
        name="Exp_Recommender",
        hypothesis_id="HYP-1",
        dataset="sp500",
        features=["market_return", "news_sentiment", "pe_ratio"],
        model="LSTM",
    )
    rec = manager.create_experiment(cfg, auto_approve=True)
    runner.run_experiment(rec.experiment_id)

    recs = ResearchRecommendationEngine.generate_recommendations(rec)
    assert len(recs) > 0
    assert "NOT TRADING OR INVESTMENT ADVICE" in recs[0]["disclaimer"]


def test_full_research_workflow():
    pipeline = ResearchIntelligencePipeline(output_report_dir="reports/research")
    out = pipeline.run_full_research_workflow(
        title="Integration Test Workflow",
        description="End to end research pipeline test",
        research_question="Does workflow run end to end?",
        expected_effect="Complete workflow execution",
        null_hypothesis="Workflow fails",
        variables=["market_return", "news_sentiment"],
        dataset="market_sp500",
        features=["market_return", "news_sentiment"],
        model="Transformer",
    )

    assert out["hypothesis"]["status"] == "SUPPORTED"
    assert out["experiment"]["status"] == "COMPLETED"
    assert "report_path" in out
