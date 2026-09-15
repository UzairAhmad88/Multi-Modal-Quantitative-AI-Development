from __future__ import annotations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from src.data.market_loader import load_market_data
from src.features.feature_fusion import FeatureBuilder
from src.models.ml.xgboost_model import QuantXGBoostModel
from src.models.ml.split import chronological_split
from src.backtesting.engine import BacktestEngine, BacktestConfig
from src.utils.logger import get_logger

logger = get_logger("script_run_backtest")


def main():
    logger.info("Executing End-to-End Quantitative Backtest...")
    market_df = load_market_data("AAPL", start="2018-01-01")

    builder = FeatureBuilder()
    raw_df, manifest = builder.build_dataset(market_df)
    df = raw_df.dropna(subset=["target_return"]).reset_index(drop=True)

    feature_cols = manifest["feature_names"]
    train_df, val_df, test_df = chronological_split(df)

    xgb = QuantXGBoostModel(mode="regression")
    xgb.fit(train_df[feature_cols], train_df["target_return"])

    preds = xgb.predict(test_df[feature_cols])
    test_df["pred_return"] = preds

    target_weights = test_df.pivot(index="date", columns="ticker", values="pred_return").fillna(0.0)

    cfg = BacktestConfig(initial_capital=100000.0, transaction_cost_bps=10.0, slippage_bps=5.0)
    engine = BacktestEngine(cfg)
    res = engine.run(market_df, target_weights)

    logger.info(f"Backtest Metrics: {res['metrics']}")


if __name__ == "__main__":
    main()
