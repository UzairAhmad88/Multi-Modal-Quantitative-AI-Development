"""
Unit & Integration Tests for Phase 20 Research Evaluation & Statistical Validation OS.
"""

import pytest
import numpy as np
from research_evaluation.metrics.return_calculator import ReturnCalculator
from research_evaluation.metrics.drawdown_analyzer import DrawdownAnalyzer
from research_evaluation.metrics.performance_metrics import PerformanceMetricsEngine
from research_evaluation.statistics.significance import SignificanceTester
from research_evaluation.statistics.bootstrap import BootstrapEngine
from research_evaluation.statistics.permutation import PermutationTester
from research_evaluation.validation.leakage_detector import LeakageDetector
from research_evaluation.walk_forward.walk_forward_engine import WalkForwardEngine
from research_evaluation.benchmarks.benchmark_engine import BenchmarkEngine
from research_evaluation.regime_analysis.regime_analyzer import RegimeAnalyzer
from research_evaluation.sensitivity.sensitivity_engine import SensitivityEngine
from research_evaluation.robustness.robustness_engine import RobustnessEngine
from research_evaluation.overfitting.overfitting_detector import OverfittingDetector
from research_evaluation.model_comparison.ablation_engine import AblationEngine
from research_evaluation.reports.research_report import ResearchReportGenerator
from research_evaluation.manager import ResearchEvaluationManager


def test_return_calculator():
    calc = ReturnCalculator()
    eq = [100.0, 105.0, 110.0, 108.0, 115.0]
    res = calc.compute_returns(eq)
    assert res["total_return"] == pytest.approx(0.15)
    assert len(res["simple_returns"]) == 4


def test_drawdown_analyzer():
    analyzer = DrawdownAnalyzer()
    eq = [100.0, 120.0, 90.0, 110.0, 130.0]  # Max DD from 120 to 90 is 30/120 = 25%
    res = analyzer.analyze_drawdowns(eq)
    assert res["max_drawdown"] == pytest.approx(0.25)
    assert res["max_duration_periods"] == 2


def test_performance_metrics():
    engine = PerformanceMetricsEngine()
    np.random.seed(42)
    rets = np.random.normal(loc=0.001, scale=0.01, size=252)
    eq = np.cumprod(1 + rets) * 100000.0

    res = engine.evaluate_performance(eq)
    assert res["cagr"] > 0
    assert res["sharpe_ratio"] > 0
    assert "sortino_ratio" in res
    assert "calmar_ratio" in res


def test_bootstrap_and_permutation():
    np.random.seed(42)
    rets = np.random.normal(loc=0.001, scale=0.01, size=100).tolist()

    boot = BootstrapEngine(num_samples=100)
    boot_res = boot.bootstrap_sharpe(rets)
    assert boot_res["ci_lower"] <= boot_res["mean_sharpe"] <= boot_res["ci_upper"]

    perm = PermutationTester(num_permutations=100)
    perm_res = perm.test_permutation(rets)
    assert 0.0 <= perm_res["permutation_p_value"] <= 1.0


def test_leakage_detector():
    detector = LeakageDetector()
    t_dec = ["2026-09-16T10:00:00Z", "2026-09-16T11:00:00Z"]
    t_avail_clean = ["2026-09-16T09:00:00Z", "2026-09-16T10:30:00Z"]
    t_avail_leaked = ["2026-09-16T09:00:00Z", "2026-09-16T11:30:00Z"]

    clean, issues = detector.check_leakage(t_dec, t_avail_clean)
    assert clean is True

    clean, issues = detector.check_leakage(t_dec, t_avail_leaked)
    assert clean is False
    assert len(issues) == 1


def test_walk_forward_engine():
    wf = WalkForwardEngine(train_period=100, validation_period=20, test_period=20, step=20)
    np.random.seed(42)
    rets = np.random.normal(loc=0.0005, scale=0.01, size=300).tolist()

    res = wf.run_walk_forward(rets)
    assert res["num_windows"] > 0
    assert "out_of_sample_sharpe" in res
    assert res["is_out_of_sample"] is True


def test_benchmark_engine():
    bench = BenchmarkEngine()
    np.random.seed(42)
    b_rets = np.random.normal(loc=0.0005, scale=0.01, size=100).tolist()
    s_rets = [r * 1.2 + 0.0002 for r in b_rets]

    res = bench.evaluate_against_benchmark(s_rets, b_rets)
    assert res["beta"] == pytest.approx(1.2, rel=1e-1)
    assert res["alpha"] > 0


def test_overfitting_detector():
    detector = OverfittingDetector()
    res = detector.evaluate_overfitting(train_sharpe=2.5, test_sharpe=0.8)

    assert res["sharpe_degradation_gap"] == pytest.approx(1.7)
    assert res["overfitting_risk_level"] == "HIGH_OVERFITTING_RISK"


def test_research_evaluation_manager_pipeline():
    mgr = ResearchEvaluationManager()
    res = mgr.evaluate_strategy(strategy_id="STRATEGY-TEST-001")

    assert res["evaluation_id"].startswith("EVAL-")
    assert res["strategy_id"] == "STRATEGY-TEST-001"
    assert "performance" in res
    assert "bootstrap" in res
    assert "walk_forward" in res
    assert "markdown_report" in res
    assert "html_report" in res
    assert "Lineage" in res["markdown_report"] or "Report" in res["markdown_report"]
