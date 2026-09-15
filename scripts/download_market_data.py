#!/usr/bin/env python3
"""
QUANT AI: Market Data Download Script
"""
from pathlib import Path
import sys
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.market_loader import load_market_data
from src.utils.logger import get_logger

logger = get_logger("download_market_data")

def main():
    parser = argparse.ArgumentParser(description="Download & Cache Market Data")
    parser.add_argument("--ticker", type=str, default="AAPL", help="Ticker symbol")
    parser.add_argument("--start", type=str, default="2018-01-01", help="Start date")
    args = parser.parse_args()

    logger.info(f"Downloading market data for {args.ticker} starting {args.start}...")
    df = load_market_data(ticker=args.ticker, start=args.start)
    logger.info(f"Downloaded {len(df)} market records for {args.ticker}.")

if __name__ == "__main__":
    main()
