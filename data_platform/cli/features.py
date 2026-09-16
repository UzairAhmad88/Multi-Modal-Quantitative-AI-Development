"""
CLI for Feature Computation.
Usage: python data_platform/cli/features.py --symbols AAPL MSFT --feature-set technical_v1
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data_platform.manager import DataPlatformManager


def main():
    parser = argparse.ArgumentParser(description="Compute quantitative features for symbols.")
    parser.add_argument("--symbols", nargs="+", default=["AAPL", "MSFT"], help="Symbols")
    parser.add_argument("--feature-set", type=str, default="technical_v1", help="Feature set name")

    args = parser.parse_args()
    mgr = DataPlatformManager()

    mkt = mgr.normalizer.normalize_market(mgr.market_source.fetch(args.symbols, "2024-01-01", "2026-09-01"))
    feats = mgr.feature_engine.compute_features(mkt)

    print(f"[SUCCESS] Computed features for {args.symbols}: {feats.shape[0]} rows, {feats.shape[1]} columns")
    print(f"Features: {list(feats.columns)}")


if __name__ == "__main__":
    main()
