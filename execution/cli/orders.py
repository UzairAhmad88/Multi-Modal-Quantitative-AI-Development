"""
CLI tool for querying and filtering Order Management System (OMS) state.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from execution.manager import ExecutionManager


def main():
    parser = argparse.ArgumentParser(description="Query OMS Orders")
    parser.add_argument("--status", type=str, default="FILLED", help="Filter by Order Status (FILLED, SUBMITTED, REJECTED)")
    args = parser.parse_args()

    mgr = ExecutionManager()
    snaps = {"AAPL": {"close": 180.0, "volume": 500000.0, "adv": 1000000.0, "volatility": 0.015}}
    mgr.run_execution(current_weights={"AAPL": 0.0}, target_weights={"AAPL": 0.2}, market_snapshots=snaps)

    orders = mgr.order_manager.get_all_orders()
    filtered = [o.to_dict() for o in orders if o.status.value == args.status.upper()]

    print(json.dumps({
        "status": "SUCCESS",
        "filter": args.status,
        "count": len(filtered),
        "orders": filtered
    }, indent=2))


if __name__ == "__main__":
    main()
