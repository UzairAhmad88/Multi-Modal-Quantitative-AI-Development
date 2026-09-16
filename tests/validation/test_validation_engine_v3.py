"""
Unit Tests for Phase 24 Statistical Validation & Research Integrity OS.
"""

import os
import pytest
import numpy as np
from validation.core.validation_manager import StatisticalValidationManager
from validation.statistics.basic_stats import BasicStatisticsCalculator
from validation.bootstrap.bootstrap_analyzer import BootstrapAnalyzer
from validation.significance.hypothesis_tester import HypothesisTester
from validation.multiple_testing.multiple_testing import MultipleTestingCorrector
from validation.stability.stability_analyzer import StabilityAnalyzer
from validation.diagnostics.overfitting_diagnostics import OverfittingDiagnostics
from validation.diagnostics.assumption_checker import AssumptionChecker
from validation.reports.validation_report_generator import ValidationReportGenerator


def test_basic_statistics_calculator():
    np.random.seed(42)
    returns = np.random.normal(loc=0.001, scale=0.01, size=200)

    moments = BasicStatisticsCalculator.calculate_moments(returns)
    assert moments["sample_size"] == 200
    assert "mean" in moments
    assert "skewness" in moments

    ci = BasicStatisticsCalculator.parametric_confidence_interval(returns)
    assert ci["lower_bound"] < ci["mean"] < ci["upper_bound"]


def test_stationary_block_bootstrap():
    np.random.seed(42)
    returns = np.random.normal(loc=0.001, scale=0.01, size=200)

    analyzer = BootstrapAnalyzer(iterations=300, block_size=10, random_seed=42)
    boot_res = analyzer.stationary_block_bootstrap(returns, np.mean, metric_name="mean_return")

    assert boot_res.lower_bound < boot_res.estimate < boot_res.upper_bound
    assert boot_res.iterations == 300
    assert boot_res.method == "stationary_block"


def test_hypothesis_tester():
    np.random.seed(42)
    returns = np.random.normal(loc=0.002, scale=0.01, size=250)

    sig_res = HypothesisTester.one_sample_t_test(returns, null_value=0.0)
    assert sig_res.sample_size == 250
    assert sig_res.p_value < 0.05
    assert sig_res.is_statistically_significant is True
    assert sig_res.effect_size > 0


def test_multiple_testing_corrector():
    p_vals = [0.001, 0.01, 0.03, 0.04, 0.15]

    bonf = MultipleTestingCorrector.bonferroni(p_vals)
    assert len(bonf.adjusted_p_values) == 5
    assert bonf.adjusted_p_values[0] == 0.005

    holm = MultipleTestingCorrector.holm(p_vals)
    assert len(holm.adjusted_p_values) == 5

    bh = MultipleTestingCorrector.benjamini_hochberg(p_vals)
    assert len(bh.adjusted_p_values) == 5


def test_stability_analyzer():
    np.random.seed(42)
    returns = np.random.normal(loc=0.0008, scale=0.01, size=500)

    stab_res = StabilityAnalyzer.analyze_subperiods(returns, num_windows=5)
    assert len(stab_res.subperiods) == 5
    assert stab_res.stability_score > 0


def test_overfitting_diagnostics_and_assumptions():
    gap_res = OverfittingDiagnostics.evaluate_generalization_gap(train_sharpe=2.5, test_sharpe=1.2)
    assert gap_res["is_high_gap"] is True
    assert len(gap_res["integrity_flags"]) >= 1

    np.random.seed(42)
    returns = np.random.normal(loc=0.001, scale=0.01, size=200)
    checks, flags = AssumptionChecker.check_all(returns, min_observations=252)
    assert len(checks) >= 2


def test_validation_manager_full_run():
    mgr = StatisticalValidationManager(storage_dir="artifacts/test_validation")

    np.random.seed(42)
    returns = np.random.normal(loc=0.001, scale=0.01, size=300)

    val = mgr.run_validation(
        experiment_id="EXP-TEST-FULL",
        returns=returns,
        train_sharpe=2.0,
        random_seed=42,
    )

    assert val.validation_id == "VAL-EXP-TEST-FULL"
    assert val.validation_status == "VALID"
    assert len(val.bootstrap_results) >= 1
    assert len(val.significance_results) >= 1

    report_md = ValidationReportGenerator.generate_report_md(val)
    assert "# Statistical Validation & Research Integrity Report" in report_md
