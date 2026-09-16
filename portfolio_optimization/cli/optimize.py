"""
CLI for Portfolio Optimization.
Usage: python portfolio_optimization/cli/optimize.py --config configs/portfolio/multimodal.yaml
"""

import argparse
import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from portfolio_optimization.manager import PortfolioOptimizationManager


def main():
    parser = argparse.ArgumentParser(description="Optimize portfolio allocation.")
    parser.add_argument("--config", type=str, default="configs/portfolio/multimodal.yaml", help="Path to portfolio YAML config")

    args = parser.parse_args()
    cfg_path = Path(args.config)
    config = {}
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    mgr = PortfolioOptimizationManager()
    signals = {"AAPL": 0.75, "MSFT": 0.60, "NVDA": 0.85, "AMZN": 0.50, "GOOGL": 0.40}

    res = mgr.optimize_portfolio(alpha_signals=signals, config=config)
    print(f"[SUCCESS] Optimized Portfolio: {res['portfolio_id']} (Status: {res['status']})")
    print(f"Target Weights: {res['entry']['weights']}")
    print(f"Expected Volatility: {res['entry']['expected_volatility']:.2%}")
    print(f"Estimated Turnover: {res['entry']['transaction_costs']['turnover']:.2%}")


if __name__ == "__main__":
    main()
