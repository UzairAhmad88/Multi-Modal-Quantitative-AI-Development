import numpy as np
import pandas as pd
from src.models.ml.split import chronological_split
from src.models.ml.xgboost_model import QuantXGBoostModel
from src.models.ml.random_forest import QuantRandomForestModel
from src.models.ml.logistic_model import QuantLinearModel
from src.evaluation.model_metrics import compute_regression_metrics, compute_classification_metrics

def test_chronological_split():
    df = pd.DataFrame({"date": pd.date_range("2023-01-01", periods=100), "val": range(100)})
    train, val, test = chronological_split(df, train_ratio=0.70, val_ratio=0.15)
    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15
    assert train["date"].max() < val["date"].min() < test["date"].min()

def test_xgboost_regression(tmp_path):
    X = pd.DataFrame({"f1": np.random.randn(100), "f2": np.random.randn(100)})
    y = X["f1"] * 2.0 + np.random.randn(100) * 0.1

    model = QuantXGBoostModel(mode="regression")
    model.fit(X, y)
    preds = model.predict(X)
    assert len(preds) == 100

    metrics = compute_regression_metrics(y, preds)
    assert metrics["rmse"] < 0.5
    assert len(model.feature_importances) == 2

    # Save and Load check
    save_path = tmp_path / "xgb.joblib"
    model.save_model(save_path)
    loaded = QuantXGBoostModel.load_model(save_path)
    loaded_preds = loaded.predict(X)
    assert np.allclose(preds, loaded_preds)

def test_ml_classification_baselines():
    X = pd.DataFrame({"f1": np.random.randn(100), "f2": np.random.randn(100)})
    y = np.where(X["f1"] > 0, 1, 0)

    for cls in [QuantLinearModel, QuantRandomForestModel, QuantXGBoostModel]:
        model = cls(mode="classification")
        model.fit(X, y)
        preds = model.predict(X)
        proba = model.predict_proba(X)
        assert len(preds) == 100
        assert proba.shape == (100, 2)
        metrics = compute_classification_metrics(y, preds)
        assert metrics["accuracy"] > 0.5
