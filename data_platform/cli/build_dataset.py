"""
CLI for Building Versioned Datasets.
Usage: python data_platform/cli/build_dataset.py --name multimodal_daily --symbols AAPL MSFT NVDA
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data_platform.manager import DataPlatformManager


def main():
    parser = argparse.ArgumentParser(description="Build versioned dataset.")
    parser.add_argument("--name", type=str, default="multimodal_daily", help="Dataset name")
    parser.add_argument("--symbols", nargs="+", default=["AAPL", "MSFT", "NVDA"], help="Symbols")

    args = parser.parse_args()
    mgr = DataPlatformManager()

    res = mgr.build_versioned_dataset(args.symbols, dataset_name=args.name)
    print(f"[SUCCESS] Dataset Build Result: {res}")


if __name__ == "__main__":
    main()
