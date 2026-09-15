#!/usr/bin/env python3
"""
QUANT AI: News Data Download Script
"""
from pathlib import Path
import sys
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.news_loader import load_news_data
from src.utils.logger import get_logger

logger = get_logger("download_news")

def main():
    parser = argparse.ArgumentParser(description="Download & Cache Financial News Data")
    parser.add_argument("--start", type=str, default="2018-01-01", help="Start date")
    args = parser.parse_args()

    tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]
    logger.info(f"Downloading news articles for universe {tickers}...")
    df = load_news_data(tickers=tickers, start=args.start)
    logger.info(f"Downloaded {len(df)} news articles.")

if __name__ == "__main__":
    main()
