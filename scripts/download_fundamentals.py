#!/usr/bin/env python3
"""
QUANT AI: Fundamental Financial Statements Download Script
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.fundamental_loader import load_fundamentals
from src.utils.logger import get_logger

logger = get_logger("download_fundamentals")

def main():
    tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]
    logger.info(f"Downloading quarterly fundamental statements for universe {tickers}...")
    df = load_fundamentals(tickers=tickers)
    logger.info(f"Loaded {len(df)} quarterly fundamental statements.")

if __name__ == "__main__":
    main()
