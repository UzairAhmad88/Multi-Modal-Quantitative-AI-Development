"""
CLI tool for running strategy backtest with full execution simulation.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from execution.manager import ExecutionManager


def main():
    parser = argparse.ArgumentParser(description="Run Backtest Execution Simulation")
    parser.add_argument("--strategy", type=str, default="STRATEGY-001", help="Strategy ID")
    parser.add_argument("--config", type=str, default="configs/execution/default.yaml", help="Path to config YAML")
    args = parser.parse_args()

    mgr = ExecutionManager()
    curr_w = {"AAPL": 0.25, "MSFT": 0.25}
    targ_w = {"AAPL": 0.50, "MSFT": 0.00}
    snaps = {
        "AAPL": {"close": 185.0, "volume": 600000.0, "adv": 1000000.0, "volatility": 0.015},
        "MSFT": {"close": 415.0, "volume": 350000.0, "adv": 800000.0, "volatility": 0.012}
    }

    res = mgr.run_execution(current_weights=curr_w, target_weights=targ_w, market_snapshots=snaps, portfolio_id=args.strategy)

    print(json.dumps({
        "status": "SUCCESS",
        "strategy_id": args.strategy,
        "execution_id": res["execution_id"],
        "total_trade_volume": res["summary_report"]["summary"]["total_trade_volume"],
        "implementation_shortfall_bps": res["summary_report"]["summary"]["total_shortfall_bps"],
        "valuation": res["valuation_after_execution"]
    }, indent=2))


if __name__ == "__main__":
    main()
