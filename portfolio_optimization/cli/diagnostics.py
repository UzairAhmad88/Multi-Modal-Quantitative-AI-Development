"""
CLI for Portfolio Diagnostics and Risk Attribution.
Usage: python portfolio_optimization/cli/diagnostics.py --portfolio PORTFOLIO-001
"""

import argparse
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from portfolio_optimization.manager import PortfolioOptimizationManager


def main():
    parser = argparse.ArgumentParser(description="Display portfolio risk attribution and diagnostics.")
    parser.add_argument("--portfolio", type=str, required=True, help="Portfolio ID")

    args = parser.parse_args()
    mgr = PortfolioOptimizationManager()
    port = mgr.get_portfolio(args.portfolio)

    if port:
        print(f"[PORTFOLIO DIAGNOSTICS] ID: {args.portfolio}")
        print(json.dumps(port, indent=2))
    else:
        print(f"[ERROR] Portfolio ID '{args.portfolio}' not found in registry.")


if __name__ == "__main__":
    main()
