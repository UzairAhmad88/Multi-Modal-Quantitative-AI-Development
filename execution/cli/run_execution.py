"""
CLI tool for running execution simulation for a target portfolio.
"""

import sys
import argparse
from pathlib import Path
import json
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from execution.manager import ExecutionManager


def main():
    parser = argparse.ArgumentParser(description="Run Execution Simulation")
    parser.add_argument("--portfolio", type=str, default="PORTFOLIO-001", help="Target portfolio ID")
    parser.add_argument("--config", type=str, default="configs/execution/default.yaml", help="Path to config YAML")
    parser.add_argument("--algo", type=str, default=None, help="Execution algorithm (MARKET, TWAP, VWAP, POV)")
    args = parser.parse_args()

    algo = args.algo
    if not algo and Path(args.config).exists():
        with open(args.config, "r") as f:
            cfg = yaml.safe_load(f)
            algo = cfg.get("execution", {}).get("algorithm", "MARKET")

    mgr = ExecutionManager(algorithm=algo or "MARKET")

    curr_w = {"AAPL": 0.2, "MSFT": 0.2, "NVDA": 0.1}
    targ_w = {"AAPL": 0.3, "MSFT": 0.1, "NVDA": 0.2, "GOOGL": 0.1}
    snaps = {
        "AAPL": {"close": 180.0, "volume": 500000.0, "adv": 1000000.0, "volatility": 0.015},
        "MSFT": {"close": 420.0, "volume": 300000.0, "adv": 800000.0, "volatility": 0.012},
        "NVDA": {"close": 130.0, "volume": 800000.0, "adv": 1500000.0, "volatility": 0.025},
        "GOOGL": {"close": 175.0, "volume": 400000.0, "adv": 900000.0, "volatility": 0.018}
    }

    res = mgr.run_execution(
        current_weights=curr_w,
        target_weights=targ_w,
        market_snapshots=snaps,
        portfolio_id=args.portfolio,
        algorithm=algo
    )

    print(json.dumps({
        "status": "SUCCESS",
        "execution_id": res["execution_id"],
        "algorithm": res["algorithm"],
        "trades_count": res["total_trades_generated"],
        "orders_count": res["child_orders_count"],
        "fills_count": res["fills_count"],
        "fill_rate": res["summary_report"]["summary"]["fill_rate"],
        "total_shortfall_dollars": res["summary_report"]["summary"]["total_shortfall_dollars"],
        "total_cost": res["cost_attribution"]["total_execution_cost"]
    }, indent=2))


if __name__ == "__main__":
    main()
