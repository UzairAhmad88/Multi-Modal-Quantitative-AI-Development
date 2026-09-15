from __future__ import annotations
from typing import Dict, List, Any
import pandas as pd
from src.features.feature_fusion import FeatureBuilder
from src.models.ml.xgboost_model import QuantXGBoostModel
from src.backtesting.engine import BacktestEngine
from src.evaluation.model_metrics import compute_regression_metrics
from src.utils.logger import get_logger

logger = get_logger("ablation")


class AblationStudyEngine:
    """Runs controlled multi-modal ablation experiments comparing individual modalities and full multi-modal fusion."""

    def run_ablation(
        self,
        market_df: pd.DataFrame,
        news_df: pd.DataFrame | None = None,
        fundamentals_df: pd.DataFrame | None = None
    ) -> Dict[str, Dict[str, Any]]:
        logger.info("Starting Multi-Modal Ablation Study...")

        experiments = {
            "Experiment A (Market Only)": (market_df, None, None),
            "Experiment B (Market + News)": (market_df, news_df, None),
            "Experiment C (Market + Fundamentals)": (market_df, None, fundamentals_df),
            "Experiment D (Market + News + Fundamentals)": (market_df, news_df, fundamentals_df)
        }

        results = {}
        builder = FeatureBuilder()
        backtester = BacktestEngine()

        for exp_name, (m, n, f) in experiments.items():
            raw_dataset, manifest = builder.build_dataset(m, n, f)

            # Filter out tail rows with NaN targets for supervised model training and evaluation
            dataset = raw_dataset.dropna(subset=["target_return"]).reset_index(drop=True)

            feature_cols = manifest["feature_names"]
            n_samples = len(dataset)
            split_idx = int(n_samples * 0.7)

            train_df = dataset.iloc[:split_idx].reset_index(drop=True)
            test_df = dataset.iloc[split_idx:].reset_index(drop=True)

            model = QuantXGBoostModel(mode="regression")
            model.fit(train_df[feature_cols], train_df["target_return"])

            preds = model.predict(test_df[feature_cols])
            reg_metrics = compute_regression_metrics(test_df["target_return"], preds)

            test_df["pred_return"] = preds
            target_weights = test_df.pivot(index="date", columns="ticker", values="pred_return").fillna(0.0)

            bt_res = backtester.run(m, target_weights)

            results[exp_name] = {
                "num_features": len(feature_cols),
                "ic": reg_metrics["ic"],
                "rmse": reg_metrics["rmse"],
                "total_return": bt_res["metrics"]["total_return"],
                "cagr": bt_res["metrics"]["cagr"],
                "sharpe": bt_res["metrics"]["sharpe_ratio"],
                "max_drawdown": bt_res["metrics"]["max_drawdown"],
                "turnover": bt_res["metrics"]["turnover"]
            }

        return results
