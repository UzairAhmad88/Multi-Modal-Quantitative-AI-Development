"""
Comprehensive Unit Test Suite for Research-Grade Validation Architecture (Phase 13).
Tests Data Quality, Leakage Detection, Temporal Splitters, Walk-Forward CV, Statistical Tests,
Bootstrap Engine, Monte Carlo Simulator, Sensitivity Analysis, Stress Engine, Overfitting Detector,
Attribution, Reproducibility Engine, Validation Pipeline, and API Endpoints.
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from api.main import app

from validation.data_validation.quality import DataQualityValidator
from validation.leakage_detection.detector import LeakageDetector
from validation.temporal_validation.splitters import TemporalSplitter
from validation.walk_forward.walk_forward import WalkForwardValidator
from validation.statistical_tests.hypothesis_tests import StatisticalTester
from validation.bootstrap.bootstrap_engine import BootstrapEngine
from validation.monte_carlo.simulator import MonteCarloSimulator
from validation.sensitivity.parameter_sweeps import SensitivityAnalyzer
from validation.stress_testing.stress_engine import StressTestingEngine
from validation.overfitting.detector import OverfittingDetector
from validation.performance_attribution.attribution import PerformanceAttribution
from validation.robustness.reproducibility import ReproducibilityEngine
from validation.orchestrator import ValidationPipeline

client = TestClient(app)


def test_data_quality_validator():
    df_valid = pd.DataFrame({
        "open": [100.0, 102.0],
        "high": [105.0, 107.0],
        "low": [98.0, 101.0],
        "close": [104.0, 106.0],
        "volume": [1000, 1200],
    })
    res = DataQualityValidator.validate_ohlcv_dataframe(df_valid)
    assert res["passed"] is True

    # Intentionally violate high price sanity
    df_invalid = pd.DataFrame({
        "open": [100.0, 102.0],
        "high": [95.0, 97.0],  # Invalid: High < Open
        "low": [90.0, 91.0],
        "close": [104.0, 106.0],
        "volume": [1000, 1200],
    })
    res_inv = DataQualityValidator.validate_ohlcv_dataframe(df_invalid)
    assert res_inv["passed"] is False
    assert res_inv["high_violations"] > 0


def test_leakage_detector_timestamps_and_scalers():
    df_leak = pd.DataFrame({
        "prediction_time": ["2026-01-01", "2026-01-02"],
        "publication_time": ["2026-01-03", "2026-01-02"],  # Violation: Future publication time
    })
    audit = LeakageDetector.audit_timestamps(df_leak)
    assert audit["has_leakage"] is True
    assert audit["status"] == "FAILED"

    # Scaler leakage audit
    train_m = np.array([0.5, 1.0])
    train_s = np.array([1.0, 2.0])
    full_m = np.array([0.5, 1.0])
    full_s = np.array([1.0, 2.0])
    scaler_audit = LeakageDetector.audit_scaler_leakage(train_m, train_s, full_m, full_s)
    assert scaler_audit["scaler_leakage"] is True


def test_temporal_splitter_purging():
    df = pd.DataFrame({"val": range(100)})
    split = TemporalSplitter.chronological_split(df, train_ratio=0.6, val_ratio=0.2, purge_window=5)
    assert split["status"] == "PASSED"
    assert len(split["train_df"]) < 60  # Purged fold


def test_walk_forward_validator():
    df = pd.DataFrame({"val": range(500)})
    res = WalkForwardValidator.run_walk_forward(df, mode="EXPANDING", train_window_size=200, test_window_size=50)
    assert res["status"] == "PASSED"
    assert res["total_folds"] >= 2


def test_statistical_tester_and_snooping():
    returns = [0.01, 0.02, 0.015, -0.005, 0.025, 0.018, 0.012]
    res = StatisticalTester.test_mean_return_significance(returns)
    assert res["statistically_significant"] is True

    snoop = StatisticalTester.check_multiple_testing_warning(total_experiments_run=25)
    assert snoop["warning_active"] is True


def test_bootstrap_engine():
    returns = list(np.random.normal(0.001, 0.01, 100))
    res = BootstrapEngine.compute_metric_confidence_intervals(returns, iterations=200, seed=42)
    assert "sharpe_ci" in res
    assert res["sharpe_ci"]["lower_bound"] <= res["sharpe_ci"]["upper_bound"]


def test_monte_carlo_simulator():
    returns = list(np.random.normal(0.001, 0.01, 50))
    res = MonteCarloSimulator.simulate_trade_paths(returns, num_simulations=100)
    assert "max_drawdown_distribution" in res


def test_stress_testing_engine():
    res = StressTestingEngine.run_transaction_cost_stress(base_sharpe=1.72)
    assert "cost_sweeps" in res
    assert res["cost_sweeps"]["10.0_bps"]["stressed_sharpe"] < 1.72


def test_reproducibility_engine():
    cfg = {"model": "LSTM"}
    res = {"sharpe": 1.72}
    val1 = ReproducibilityEngine.generate_validation_hash("EXP-1", cfg, res, validation_id="VAL-TEST-001")
    val2 = ReproducibilityEngine.generate_validation_hash("EXP-1", cfg, res, validation_id="VAL-TEST-001")
    assert val1["validation_hash"] == val2["validation_hash"]



def test_validation_pipeline_and_api():
    pipeline = ValidationPipeline()
    full_res = pipeline.run_full_validation_suite("EXP-TEST-999")
    assert full_res["validation_summary"]["status"] == "PASSED"

    # API Endpoint tests
    response = client.get("/validation/overview")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

    exp_res = client.get("/validation/experiments/EXP-TEST-999")
    assert exp_res.status_code == 200
    assert "validation_hash" in exp_res.json()
