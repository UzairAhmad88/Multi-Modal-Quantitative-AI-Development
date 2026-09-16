"""
CLI Script: Compare metrics of two or more quantitative models side by side.
Usage: python models/compare.py MODEL-001 MODEL-002
"""

from __future__ import annotations
import argparse
import sys
from models.evaluation.comparison import ModelComparisonEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Quantitative Models")
    parser.add_argument("models", nargs="+", help="List of Model IDs to compare")
    args = parser.parse_args()

    engine = ModelComparisonEngine()
    res = engine.compare_models(args.models)

    print("=" * 80)
    print(f"MODEL COMPARISON ({len(args.models)} Models)")
    print("=" * 80)
    print(f"{'Model ID':<22} {'Type':<15} {'Status':<12} {'Sharpe':<10} {'MAE'}")
    print("-" * 80)
    for m_id, data in res.get("comparison", {}).items():
        m_type = str(data.get("type", "N/A"))
        status = str(data.get("status", "N/A"))
        sharpe = str(data.get("sharpe", "N/A"))
        mae = str(data.get("mae", "N/A"))
        print(f"{m_id:<22} {m_type:<15} {status:<12} {sharpe:<10} {mae}")
    print("-" * 80)
    print("Note: Quantitative model metrics are evaluated independently without universal single scores.")


if __name__ == "__main__":
    main()
