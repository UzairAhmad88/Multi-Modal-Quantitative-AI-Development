from __future__ import annotations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from src.data.market_loader import load_market_data
from src.features.feature_fusion import FeatureBuilder
from src.models.ml.xgboost_model import QuantXGBoostModel
from src.models.ml.split import chronological_split
from src.evaluation.model_metrics import compute_regression_metrics
from src.utils.paths import MODELS_DIR
from src.utils.logger import get_logger

logger = get_logger("script_train_ml")


def main():
    logger.info("Training Tabular Machine Learning Models...")
    market_df = load_market_data("AAPL", start="2018-01-01")

    builder = FeatureBuilder()
    raw_df, manifest = builder.build_dataset(market_df)
    df = raw_df.dropna(subset=["target_return"]).reset_index(drop=True)

    feature_cols = manifest["feature_names"]
    train_df, val_df, test_df = chronological_split(df)

    xgb = QuantXGBoostModel(mode="regression")
    xgb.fit(train_df[feature_cols], train_df["target_return"])

    preds = xgb.predict(test_df[feature_cols])
    metrics = compute_regression_metrics(test_df["target_return"], preds)
    logger.info(f"XGBoost Test Metrics: {metrics}")

    save_path = MODELS_DIR / "trained" / "xgboost_v1.joblib"
    xgb.save_model(save_path)
    logger.info(f"Saved model to {save_path}")


if __name__ == "__main__":
    main()
