"""
Unit and Integration Test Suite for Model Monitoring, Drift Detection & Research Health OS (Phase 28).
"""

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from monitoring.data_drift.psi import calculate_psi
from monitoring.data_drift.ks_test import calculate_ks_test
from monitoring.data_drift.distance import calculate_wasserstein_distance
from monitoring.data_drift.detector import DataDriftDetector
from monitoring.feature_drift.importance_shift import calculate_importance_shift
from monitoring.feature_drift.correlation_shift import calculate_correlation_matrix_shift
from monitoring.concept_drift.ddm import DDM
from monitoring.concept_drift.eddm import EDDM
from monitoring.concept_drift.page_hinkley import PageHinkley
from monitoring.performance.accuracy_decay import calculate_accuracy_decay
from monitoring.performance.alpha_decay import AlphaDecayTracker, calculate_alpha_ic_decay
from monitoring.performance.sharpe_decay import calculate_sharpe_decay
from monitoring.regime.detector import RegimeChangeDetector
from monitoring.health.research_health import calculate_research_health_score
from monitoring.core.monitor_engine import ModelMonitorEngine
from monitoring.services.monitoring_service import MonitoringService
from api.main import app


def test_psi_and_ks_calculation():
    np.random.seed(42)
    b_vals = np.random.normal(0.0, 1.0, 500)
    t_vals_identical = np.random.normal(0.0, 1.0, 500)
    t_vals_drifted = np.random.normal(2.0, 1.0, 500)

    psi_identical = calculate_psi(b_vals, t_vals_identical)
    psi_drifted = calculate_psi(b_vals, t_vals_drifted)

    assert psi_identical < 0.10
    assert psi_drifted > 0.25

    ks_stat_id, ks_pval_id = calculate_ks_test(b_vals, t_vals_identical)
    ks_stat_dr, ks_pval_dr = calculate_ks_test(b_vals, t_vals_drifted)

    assert ks_pval_id > 0.05
    assert ks_pval_dr < 0.01


def test_wasserstein_distance():
    b_vals = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    t_vals = np.array([2.0, 3.0, 4.0, 5.0, 6.0])

    dist = calculate_wasserstein_distance(b_vals, t_vals)
    assert abs(dist - 1.0) < 1e-4


def test_data_drift_detector():
    np.random.seed(42)
    b_df = pd.DataFrame({
        "volatility": np.random.normal(0.01, 0.002, 200),
        "sentiment": np.random.normal(0.10, 0.05, 200),
    })
    t_df = pd.DataFrame({
        "volatility": np.random.normal(0.05, 0.01, 200),  # Drifted
        "sentiment": np.random.normal(0.10, 0.05, 200),   # Stable
    })

    detector = DataDriftDetector(psi_warning_threshold=0.10, psi_critical_threshold=0.25)
    results = detector.evaluate_feature_drift(b_df, t_df)

    res_map = {r.feature_name: r for r in results}
    assert res_map["volatility"].is_drifted
    assert res_map["volatility"].severity == "SIGNIFICANT"
    assert not res_map["sentiment"].is_drifted


def test_feature_importance_and_correlation_shift():
    b_imp = {"feat1": 0.50, "feat2": 0.30, "feat3": 0.20}
    t_imp = {"feat1": 0.48, "feat2": 0.31, "feat3": 0.21}

    cosine_sim, rank_corr, top_k = calculate_importance_shift(b_imp, t_imp)
    assert cosine_sim > 0.99
    assert rank_corr > 0.99

    b_df = pd.DataFrame({"f1": [1, 2, 3, 4], "f2": [2, 4, 6, 8]})
    t_df = pd.DataFrame({"f1": [1, 2, 3, 4], "f2": [8, 6, 4, 2]})  # Inverted correlation

    f_norm, max_s, mean_s = calculate_correlation_matrix_shift(b_df, t_df)
    assert max_s > 1.5


def test_concept_drift_detectors():
    # Test DDM
    ddm = DDM(min_num_instances=10)
    errors = np.concatenate([np.zeros(20), np.ones(30)])  # Sudden error increase
    any_warn, any_drift, drift_idx = ddm.run_batch(errors)
    assert any_drift
    assert drift_idx > 0

    # Test Page-Hinkley
    ph = PageHinkley(threshold=10.0)
    vals = np.concatenate([np.zeros(20), np.ones(50) * 10.0])
    ph_drift, ph_idx = ph.run_batch(vals)
    assert ph_drift
    assert ph_idx > 0


def test_alpha_decay_tracker():
    np.random.seed(42)
    b_sig = np.random.normal(0, 1, 200)
    b_ret = np.zeros(200)
    b_ret[1:] = b_sig[:-1] * 0.20 + np.random.normal(0, 0.02, 199)  # Strong lag-1 predictive IC

    t_sig = np.random.normal(0, 1, 200)
    t_ret = np.random.normal(0, 0.05, 200)  # No signal (Decayed)

    tracker = AlphaDecayTracker()
    res = tracker.evaluate_alpha_decay(b_sig, b_ret, t_sig, t_ret)

    assert res.ic_decay_pct > 0.30
    assert res.is_decay_flagged



def test_regime_change_detector():
    np.random.seed(42)
    b_rets = np.random.normal(0.001, 0.01, 200)
    t_rets = np.random.normal(-0.005, 0.04, 200)  # High vol bear regime

    detector = RegimeChangeDetector(jump_threshold=2.0)
    res = detector.detect_regime_shift(b_rets, t_rets)

    assert res.is_regime_shift_detected
    assert res.volatility_jump_ratio > 2.0


def test_model_monitor_engine_full_audit():
    np.random.seed(42)
    b_df = pd.DataFrame({"market_volatility": np.random.normal(0.01, 0.002, 200)})
    t_df = pd.DataFrame({"market_volatility": np.random.normal(0.03, 0.005, 200)})

    engine = ModelMonitorEngine()
    res = engine.run_monitoring_audit("EXP-TEST-001", b_df, t_df)

    assert res.monitoring_id.startswith("MON-")
    assert res.health_score.overall_health_score < 100.0
    assert len(res.alerts) > 0


def test_monitoring_service_persistence():
    service = MonitoringService()
    res = service.run_monitoring("EXP-SERVICE-TEST")

    fetched = service.get_monitoring_run(res.monitoring_id)
    assert fetched is not None
    assert fetched.monitoring_id == res.monitoring_id
    assert fetched.experiment_id == "EXP-SERVICE-TEST"

    runs = service.list_monitoring_runs()
    assert len(runs) > 0


def test_monitoring_api_endpoints():
    client = TestClient(app)

    # Test GET health endpoint
    h_resp = client.get("/monitoring/health")
    assert h_resp.status_code == 200
    assert h_resp.json()["status"] == "healthy"

    # Test POST run endpoint
    r_resp = client.post("/monitoring/run", json={"experiment_id": "EXP-API-TEST"})
    assert r_resp.status_code == 200
    data = r_resp.json()
    assert "monitoring_id" in data
    assert data["experiment_id"] == "EXP-API-TEST"

    # Test POST drift check endpoint
    d_resp = client.post(
        "/monitoring/drift-check",
        json={
            "feature_name": "market_volatility",
            "baseline_values": [1.0, 2.0, 3.0, 4.0, 5.0] * 10,
            "target_values": [10.0, 20.0, 30.0, 40.0, 50.0] * 10,
        },
    )
    assert d_resp.status_code == 200
    assert d_resp.json()["is_drifted"]
