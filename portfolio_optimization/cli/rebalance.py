"""
CLI for Rebalancing Orders.
Usage: python portfolio_optimization/cli/rebalance.py --portfolio PORTFOLIO-001
"""

import argparse
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from portfolio_optimization.manager import PortfolioOptimizationManager
from portfolio_optimization.portfolio.rebalancer import RebalancingEngine


def main():
    parser = argparse.ArgumentParser(description="Generate rebalancing order quantities.")
    parser.add_argument("--portfolio", type=str, required=True, help="Target Portfolio ID")

    args = parser.parse_args()
    mgr = PortfolioOptimizationManager()
    port = mgr.get_portfolio(args.portfolio)

    if not port:
        print(f"[ERROR] Portfolio ID '{args.portfolio}' not found.")
        return

    curr_weights = {"AAPL": 0.20, "MSFT": 0.20, "NVDA": 0.20, "AMZN": 0.20, "GOOGL": 0.20}
    targ_weights = port["weights"]
    prices = {"AAPL": 180.0, "MSFT": 410.0, "NVDA": 120.0, "AMZN": 175.0, "GOOGL": 165.0}

    rebalancer = RebalancingEngine()
    orders = rebalancer.generate_rebalance_orders(curr_weights, targ_weights, prices)

    print(f"[REBALANCE ORDERS] Summary for {args.portfolio}:")
    print(json.dumps(orders, indent=2))


if __name__ == "__main__":
    main()
