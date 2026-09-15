from __future__ import annotations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.market_loader import load_market_data
from src.data.news_loader import load_news_data
from src.data.fundamental_loader import load_fundamentals
from src.features.feature_fusion import FeatureBuilder
from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger("script_build_features")


def main():
    config = get_config()
    universe = config.get("data.universe", ["AAPL", "MSFT", "NVDA"])
    logger.info(f"Building features for universe: {universe}")

    market_dfs = [load_market_data(t, start="2018-01-01") for t in universe]
    import pandas as pd
    market_df = pd.concat(market_dfs, ignore_index=True)
    news_df = load_news_data(tickers=universe, start="2018-01-01")
    fund_df = load_fundamentals()

    builder = FeatureBuilder()
    df_fused, manifest = builder.build_dataset(market_df, news_df, fund_df)

    logger.info(f"Built feature dataset with {len(df_fused)} rows and {len(manifest['feature_names'])} features.")


if __name__ == "__main__":
    main()
