"""
CLI for Data Ingestion.
Usage: python data_platform/cli/ingest.py --source market --symbols AAPL MSFT
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data_platform.manager import DataPlatformManager


def main():
    parser = argparse.ArgumentParser(description="Ingest quantitative market, news, or fundamental data.")
    parser.add_argument("--source", type=str, required=True, choices=["market", "news", "fundamentals"], help="Data source to ingest")
    parser.add_argument("--symbols", nargs="+", default=["AAPL", "MSFT", "NVDA"], help="Ticker symbols")

    args = parser.parse_args()
    mgr = DataPlatformManager()

    if args.source == "market":
        res = mgr.ingest_market_data(args.symbols)
    elif args.source == "news":
        res = mgr.ingest_news_data(args.symbols)
    else:
        res = mgr.ingest_fundamental_data(args.symbols)

    print(f"[SUCCESS] Ingested {args.source} data: {res}")


if __name__ == "__main__":
    main()
