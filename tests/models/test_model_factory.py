"""
Comprehensive Test Suite for Phase 16 - Model Factory, Model Registry & Controlled Model Lifecycle.
"""

import os
import shutil
import tempfile
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from models.factory.factory import ModelFactory
from models.registry.registry import ModelRegistry, ModelStatus
from models.training.trainer import ModelTrainingEngine
from models.evaluation.evaluator import ModelEvaluator
from models.evaluation.comparison import ModelComparisonEngine
from models.ensemble.ensemble_model import EnsembleEngine
from models.lifecycle.promoter import ModelPromoter
from models.lifecycle.rollback import ModelRollbackManager
from models.monitoring.drift_detector import ModelDriftDetector
from models.monitoring.retraining_manager import ModelRetrainingManager
from models.utils.hardware import HardwareDetector


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_config():
    return {
        "model": {
            "name": "unit_test_xgboost",
            "type": "xgboost",
            "version": "1.0.0",
            "task": "regression"
        },
        "training": {
            "seed": 42
        },
        "data": {
            "dataset": "DS-TEST"
        }
    }


def test_model_factory_instantiation():
    types = ["logistic_regression", "random_forest", "xgboost", "lstm", "gru", "transformer", "multimodal", "ensemble"]
    for t in types:
        cfg = {"model": {"name": f"test_{t}", "type": t, "version": "1.0.0"}}
        model = ModelFactory.create_model(cfg)
        assert model is not None
        assert model.model_id.startswith("MODEL-")


def test_base_model_interface(sample_config):
    model = ModelFactory.create_model(sample_config)
    X = np.random.normal(0, 1, (20, 16))
    y = np.random.normal(0, 1, 20)

    model.fit(X, y)
    preds = model.predict(X)
    assert len(preds) == 20
    meta = model.get_metadata()
    assert meta["name"] == "unit_test_xgboost"


def test_model_training_engine(sample_config, temp_dir):
    reg_file = str(Path(temp_dir) / "registry.json")
    art_dir = str(Path(temp_dir) / "trained")

    trainer = ModelTrainingEngine(artifact_dir=art_dir, registry_file=reg_file)
    res = trainer.train_model(sample_config)

    assert res["status"] == "COMPLETED"
    assert "model_id" in res
    assert Path(res["artifact_path"]).exists()
    assert "mae" in res["metrics"]


def test_model_serialization(sample_config, temp_dir):
    model = ModelFactory.create_model(sample_config)
    X = np.random.normal(0, 1, (20, 16))
    y = np.random.normal(0, 1, 20)
    model.fit(X, y)

    save_path = str(Path(temp_dir) / "model.pkl")
    model.save(save_path)
    assert Path(save_path).exists()

    loaded = model.load(save_path)
    assert loaded is not None


def test_model_registry_versioning(temp_dir):
    reg_file = str(Path(temp_dir) / "registry.json")
    reg = ModelRegistry(registry_file=reg_file)

    reg.register_model("M1", "TestModel", "1.0.0", "xgboost")
    reg.register_model("M2", "TestModel", "1.1.0", "xgboost")

    m1 = reg.get_model("M1")
    m2 = reg.get_model("M2")
    assert m1["version"] == "1.0.0"
    assert m2["version"] == "1.1.0"


def test_model_promotion_and_gates(temp_dir):
    reg_file = str(Path(temp_dir) / "registry.json")
    promoter = ModelPromoter(registry_file=reg_file)

    promoter.registry.register_model("M1", "TestModel", "1.0.0", "xgboost")

    # Passing gate
    res1 = promoter.evaluate_and_promote("M1", ModelStatus.CANDIDATE, {"leakage_check": "PASS", "validation": "PASS"})
    assert res1["status"] == "PROMOTED"

    # Failing gate
    promoter.registry.register_model("M2", "TestModel", "1.0.0", "xgboost")
    res2 = promoter.evaluate_and_promote("M2", ModelStatus.CANDIDATE, {"leakage_check": "FAIL", "validation": "FAIL"})
    assert res2["status"] == "REJECTED"


def test_champion_challenger_and_rollback(temp_dir):
    reg_file = str(Path(temp_dir) / "registry.json")
    rb = ModelRollbackManager(registry_file=reg_file)

    rb.registry.register_model("M1", "Champ", "1.0.0", "xgboost", status=ModelStatus.PAPER)
    rb.registry.register_model("M2", "Champ", "1.1.0", "xgboost", status=ModelStatus.CANDIDATE)

    rb.registry.set_champion("M2")
    assert rb.registry.get_champion()["model_id"] == "M2"

    res = rb.rollback()
    assert res["status"] == "SUCCESS"
    assert res["restored_champion"] == "M1"


def test_model_comparison_engine(temp_dir):
    reg_file = str(Path(temp_dir) / "registry.json")
    mce = ModelComparisonEngine(registry_file=reg_file)
    mce.registry.register_model("M1", "Model1", "1.0.0", "xgboost")
    mce.registry.register_model("M2", "Model2", "1.0.0", "lstm")

    comp = mce.compare_models(["M1", "M2"])
    assert comp["status"] == "SUCCESS"
    assert "M1" in comp["comparison"]

    ablation = mce.compare_ablation("M1")
    assert "market_only" in ablation["ablation_results"]


def test_ensemble_engine():
    ee = EnsembleEngine()
    p1 = np.array([0.1, 0.2, 0.3])
    p2 = np.array([0.2, 0.4, 0.6])

    res_avg = ee.combine_predictions([p1, p2], ensemble_type="weighted_average", weights=[0.5, 0.5])
    assert len(res_avg) == 3
    assert np.isclose(res_avg[0], 0.15)


def test_drift_detector():
    dd = ModelDriftDetector()
    ref = np.random.normal(0, 1, 100)
    curr_same = np.random.normal(0, 1, 100)
    curr_drift = np.random.normal(5, 1, 100)

    res_same = dd.detect_drift(ref, curr_same)
    assert not res_same["drift_detected"]

    res_drift = dd.detect_drift(ref, curr_drift)
    assert res_drift["drift_detected"]


def test_retraining_manager(temp_dir):
    rm = ModelRetrainingManager(enabled=False)
    res = rm.trigger_retraining("M1", reason="SCHEDULED")
    assert res["status"] == "DISABLED"


def test_hardware_detector():
    info = HardwareDetector.get_device_info()
    assert "device" in info
    assert "cpu_cores" in info
