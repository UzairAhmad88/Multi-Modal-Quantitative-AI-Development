from __future__ import annotations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.market_loader import load_market_data
from src.data.news_loader import load_news_data
from src.data.fundamental_loader import load_fundamentals
from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger("script_download_data")


def main():
    config = get_config()
    universe = config.get("data.universe", ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"])
    logger.info(f"Downloading/generating raw multi-modal datasets for universe: {universe}")

    for ticker in universe:
        df_mkt = load_market_data(ticker, start="2018-01-01")
        logger.info(f"Loaded {len(df_mkt)} market bars for {ticker}")

    df_news = load_news_data(tickers=universe, start="2018-01-01")
    logger.info(f"Loaded {len(df_news)} news items")

    df_fund = load_fundamentals()
    logger.info(f"Loaded {len(df_fund)} quarterly fundamental statements")

    logger.info("Data download script completed successfully.")


if __name__ == "__main__":
    main()
