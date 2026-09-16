"""
Unit & Integration Test Suite for Phase 27 Walk-Forward Validation & OOS OS.
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from validation.temporal.windows import ValidationWindow
from validation.temporal.timeline import TimelineValidator
from validation.walk_forward.expanding import ExpandingWindowGenerator
from validation.walk_forward.rolling import RollingWindowGenerator
from validation.walk_forward.anchored import AnchoredWindowGenerator
from validation.purged.splitter import PurgedTimeSeriesSplitter
from validation.purged.purge import LabelHorizonPurger
from validation.purged.embargo import EmbargoExcluder
from validation.leakage.detector import LeakageDetector
from validation.oos.evaluator import OOSEvaluator
from validation.robustness.stability import StabilityAnalyzer
from validation.core.test_lock import TestSetLockEngine, TestSetLockedError
from validation.core.validation_engine import AdvancedWalkForwardEngine
from validation.services.walk_forward_service import WalkForwardService


def test_validation_window_bounds():
    w_valid = ValidationWindow(
        window_id="W1",
        fold_index=1,
        train_start="2022-01-01",
        train_end="2022-06-30",
        validation_start="2022-07-01",
        validation_end="2022-08-31",
        test_start="2022-09-01",
        test_end="2022-10-31",
    )
    check = w_valid.validate_temporal_ordering()
    assert check["is_valid"] is True


def test_timeline_validator():
    dates = pd.date_range("2022-01-01", periods=100, freq="D")
    df = pd.DataFrame({"timestamp": dates, "availability_timestamp": dates - pd.Timedelta(days=1)})
    res = TimelineValidator.audit_timeline(df)
    assert res["status"] == "PASSED"
    assert res["is_sorted"] is True
    assert res["availability_violations"] == 0


def test_expanding_window_generator():
    dates = pd.date_range("2022-01-01", periods=500, freq="B")
    df = pd.DataFrame({"timestamp": dates.strftime("%Y-%m-%d")})
    folds = ExpandingWindowGenerator.generate_folds(df, initial_train_size=200, val_size=50, test_size=50, step_size=50)
    assert len(folds) >= 2
    assert folds[0].train_samples == 200
    assert folds[1].train_samples == 250  # Expanding


def test_rolling_window_generator():
    dates = pd.date_range("2022-01-01", periods=500, freq="B")
    df = pd.DataFrame({"timestamp": dates.strftime("%Y-%m-%d")})
    folds = RollingWindowGenerator.generate_folds(df, train_size=200, val_size=50, test_size=50, step_size=50)
    assert len(folds) >= 2
    assert folds[0].train_samples == 200
    assert folds[1].train_samples == 200  # Rolling fixed window


def test_purged_time_series_splitter():
    dates = pd.date_range("2022-01-01", periods=300, freq="B")
    df = pd.DataFrame({"timestamp": dates})
    split_res = PurgedTimeSeriesSplitter.split(df, n_splits=3, label_horizon_steps=5, embargo_steps=5)
    assert split_res["status"] == "PASSED"
    assert len(split_res["folds"]) == 3
    for fold in split_res["folds"]:
        assert fold["purged_count"] >= 0


def test_leakage_detector_clean():
    dates = pd.date_range("2022-01-01", periods=200, freq="B")
    df = pd.DataFrame({
        "timestamp": dates.strftime("%Y-%m-%d"),
        "availability_timestamp": (dates - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
        "feature_1": np.random.normal(0, 1, 200),
        "target": np.random.normal(0, 1, 200),
    })
    res = LeakageDetector.audit_full_dataset(df, decision_col="timestamp", target_col="target")
    assert res["has_leakage"] is False


def test_leakage_detector_future_timestamp():
    dates = pd.date_range("2022-01-01", periods=200, freq="B")
    # Intentional future leakage timestamp
    future_dates = dates + pd.Timedelta(days=5)
    df = pd.DataFrame({
        "timestamp": dates.strftime("%Y-%m-%d"),
        "feature_timestamp": future_dates.strftime("%Y-%m-%d"),
        "target": np.random.normal(0, 1, 200),
    })
    res = LeakageDetector.audit_full_dataset(df, decision_col="timestamp", target_col="target")
    assert res["has_leakage"] is True


def test_oos_evaluator():
    np.random.seed(42)
    y_true = np.random.normal(0, 1, 50)
    y_pred = y_true + np.random.normal(0, 0.1, 50)
    returns = np.random.normal(0.001, 0.01, 50)
    ev = OOSEvaluator.evaluate_fold("F1", y_true, y_pred, fold_returns=returns)
    assert ev["prediction_metrics"]["mae"] > 0
    assert ev["trading_metrics"]["sharpe_ratio"] > 0


def test_stability_analyzer():
    sharpes = [1.5, 1.2, 1.8, 1.4, 1.6]
    res = StabilityAnalyzer.evaluate_performance_stability(sharpes)
    assert res["status"] in ["HIGH_STABILITY", "MODERATE"]
    assert res["positive_fold_ratio"] == 1.0


def test_test_set_lock_engine(tmp_path):
    lock_engine = TestSetLockEngine(storage_dir=str(tmp_path))
    exp_id = "EXP-TEST-LOCK"
    config_hash = "hash12345"

    # Initially unlocked
    perm = lock_engine.verify_access_permission(exp_id, config_hash)
    assert perm["allowed"] is True

    # Lock test set
    lock_engine.lock_test_set(exp_id, config_hash)

    # Permission allowed for matching hash
    perm2 = lock_engine.verify_access_permission(exp_id, config_hash)
    assert perm2["allowed"] is True

    # Permission denied for altered hash
    with pytest.raises(TestSetLockedError):
        lock_engine.verify_access_permission(exp_id, "different_hash_999")


def test_walk_forward_service_full_flow():
    service = WalkForwardService(storage_dir="artifacts/test_validation_wf")
    res = service.run_walk_forward("EXP-SERVICE-TEST", method="EXPANDING")
    assert res["validation_id"].startswith("VAL-EXP-SERVICE-TEST")
    assert res["status"] in ["COMPLETED", "WARNING"]
    assert "oos_metrics" in res


def test_walk_forward_api_endpoints():
    from api.main import app
    test_client = TestClient(app)
    res = test_client.get("/walk-forward-v2/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

    run_res = test_client.post("/walk-forward-v2/run", json={"experiment_id": "EXP-API-TEST", "method": "EXPANDING"})
    assert run_res.status_code == 200
    data = run_res.json()
    val_id = data["validation_id"]

    val_res = test_client.get(f"/walk-forward-v2/{val_id}")
    assert val_res.status_code == 200

    metrics_res = test_client.get(f"/walk-forward-v2/{val_id}/metrics")
    assert metrics_res.status_code == 200
