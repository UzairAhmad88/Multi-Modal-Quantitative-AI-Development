"""
CLI for Comparing Portfolios.
Usage: python portfolio_optimization/cli/compare.py --portfolios PORTFOLIO-001 PORTFOLIO-002
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from portfolio_optimization.manager import PortfolioOptimizationManager


def main():
    parser = argparse.ArgumentParser(description="Compare portfolio metrics and allocations side-by-side.")
    parser.add_argument("--portfolios", nargs="+", required=True, help="Portfolio IDs to compare")

    args = parser.parse_args()
    mgr = PortfolioOptimizationManager()

    print(f"[PORTFOLIO COMPARISON] ({len(args.portfolios)} Portfolios)")
    print(f"{'Portfolio ID':<25} | {'Method':<20} | {'Expected Vol':<12} | {'Turnover':<10}")
    print("-" * 75)

    for pid in args.portfolios:
        p = mgr.get_portfolio(pid)
        if p:
            vol = p.get("expected_volatility", 0.0)
            turnover = p.get("transaction_costs", {}).get("turnover", 0.0)
            print(f"{pid:<25} | {p['method']:<20} | {vol:<12.2%} | {turnover:<10.2%}")
        else:
            print(f"{pid:<25} | {'NOT FOUND':<20} | {'N/A':<12} | {'N/A':<10}")


if __name__ == "__main__":
    main()
