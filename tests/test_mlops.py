"""
Test Suite for Phase 8 MLOps, Experiment Tracking & Model Registry Engine
Tests Dataset Registry, Feature Registry, Model Registry, Experiment Manager,
Lineage Tracker, Leakage Validator, Metric Store, and Reproducibility Engine.
"""

import os
import shutil
import tempfile
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.mlops.experiments import ExperimentManager
from src.mlops.datasets import DatasetRegistry
from src.mlops.features import FeatureRegistry
from src.mlops.models import ModelRegistry
from src.mlops.strategies import StrategyRegistry
from src.mlops.lineage import LineageTracker
from src.mlops.leakage_validator import LeakageValidator
from src.mlops.metrics_store import MetricStore
from src.mlops.reproducer import ReproducibilityValidator, ExperimentReproducer
from src.mlops.pipelines import FullResearchPipeline


def test_experiment_manager():
    mgr = ExperimentManager()
    exp = mgr.create_experiment("test_exp", "Test experiment description", {"seed": 42})
    assert exp["experiment_id"].startswith("EXP-")
    assert exp["status"] == "PLANNED"
    assert "hardware_metadata" in exp
    assert "git_commit" in exp

    fetched = mgr.get_experiment(exp["experiment_id"])
    assert fetched["experiment_name"] == "test_exp"

    run_info = mgr.start_run(exp["experiment_id"], {"lr": 0.01})
    assert run_info["status"] == "RUNNING"
    assert run_info["run_id"].startswith("EXP-RUN-")

    completed = mgr.finish_run(run_info["run_id"], metrics={"predictive.rmse": 0.015}, status="COMPLETED")
    assert completed["status"] == "COMPLETED"


def test_dataset_registry():
    reg = DatasetRegistry()
    ds = reg.register_dataset(
        name="test_sp500",
        version="v1.0.0",
        source="unit_test",
        symbols=["AAPL", "MSFT"],
        df=pd.DataFrame({"close": [150.0, 155.0], "volume": [1000, 1200]})
    )
    assert ds["dataset_id"].startswith("DS-")
    assert ds["checksum"] != ""
    assert "quality_report" in ds

    fetched = reg.get_dataset(ds["dataset_id"])
    assert fetched["name"] == "test_sp500"


def test_feature_registry():
    reg = FeatureRegistry()
    feat = reg.register_feature(
        feature_name="return_1d",
        feature_group="momentum",
        definition="1-day percentage price change",
        formula="close.pct_change(1)",
        source="close",
        version="v1.0.0"
    )
    assert feat["feature_id"].startswith("FEAT-")
    assert feat["feature_group"] == "momentum"
    assert feat["lineage"]["raw_data"] == "close"

    fetched = reg.get_feature(feat["feature_id"])
    assert fetched["feature_name"] == "return_1d"


def test_model_registry_and_promotion():
    reg = ModelRegistry()
    m = reg.register_model(
        model_name="XGBoostAlpha",
        model_type="XGBoost",
        version="v1.0.0",
        framework="xgboost",
        metrics={"predictive.rmse": 0.02, "trading.sharpe_ratio": 1.5}
    )
    assert m["model_id"].startswith("MODEL-")
    assert m["status"] == "EXPERIMENTAL"
    assert m["signature"]["input_features"] == []

    # Update status promotion
    updated = reg.update_status(m["model_id"], "VALIDATED")
    assert updated["status"] == "VALIDATED"

    promoted = reg.update_status(m["model_id"], "PAPER")
    assert promoted["status"] == "PAPER"

    archived = reg.update_status(m["model_id"], "ARCHIVED")
    assert archived["status"] == "ARCHIVED"


def test_strategy_registry():
    reg = StrategyRegistry()
    strat = reg.register_strategy(
        strategy_name="MeanVarianceAlpha",
        signal_logic="Top decile alpha longs",
        portfolio_method="mean_variance",
        version="v1.0.0"
    )
    assert strat["strategy_id"].startswith("STRAT-")
    assert strat["portfolio_method"] == "mean_variance"


def test_lineage_tracker():
    tracker = LineageTracker()
    run_id = "EXP-RUN-TEST-001"
    tracker.record_node(run_id, "dataset", {"name": "sp500", "version": "v1.0.0"})
    tracker.record_node(run_id, "feature", {"name": "mom_vol", "version": "v1.0.0"})
    tracker.record_node(run_id, "model", {"name": "LSTM", "version": "v1.0.0"})

    lineage = tracker.get_lineage(run_id)
    assert len(lineage["nodes"]) == 3
    assert "dataset" in lineage["nodes"]
    assert "model" in lineage["nodes"]


def test_leakage_validator():
    validator = LeakageValidator()

    # Valid dataframe with point in time
    dates = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame({
        "timestamp": dates,
        "feature_1": np.random.randn(10),
        "target": np.random.randn(10)
    })

    val_res = validator.validate_point_in_time(df, timestamp_col="timestamp")
    assert val_res["has_leakage"] == False

    horizon_res = validator.validate_target_alignment(df, feature_cols=["feature_1"], target_col="target", horizon=1)
    assert horizon_res["is_aligned"] == True


def test_metric_store():
    store = MetricStore()
    store.log_metrics("EXP-RUN-TEST-001", {
        "predictive.rmse": 0.014,
        "predictive.mae": 0.010,
        "trading.sharpe_ratio": 1.75,
        "risk.var_95": -0.018
    })

    run_metrics = store.get_run_metrics("EXP-RUN-TEST-001")
    assert run_metrics["predictive.rmse"] == 0.014
    assert run_metrics["trading.sharpe_ratio"] == 1.75
    assert run_metrics["risk.var_95"] == -0.018


def test_reproducibility_engine():
    validator = ReproducibilityValidator()
    audit = validator.audit_run("EXP-RUN-001")
    assert audit["is_reproducible"] == True
    assert audit["missing_artifacts"] == []

    repro = ExperimentReproducer()
    res = repro.reproduce("EXP-RUN-001")
    assert res["match_status"] in ["EXACT_MATCH", "TOLERANCE_MATCH"]


def test_full_research_pipeline():
    config_path = "configs/experiments/multimodal.yaml"
    pipeline = FullResearchPipeline(config_path=config_path)
    results = pipeline.run()

    assert results["status"] == "COMPLETED"
    assert results["run_id"].startswith("EXP-RUN-")
    assert Path(results["report_path"]).exists()
