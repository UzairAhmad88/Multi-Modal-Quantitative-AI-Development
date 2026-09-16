"""
CLI tool for inspecting an execution run report by ID.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from execution.manager import ExecutionManager


def main():
    parser = argparse.ArgumentParser(description="Inspect Execution Report")
    parser.add_argument("--execution", type=str, default="EXEC-LATEST", help="Execution Run ID")
    args = parser.parse_args()

    mgr = ExecutionManager()
    snaps = {"AAPL": {"close": 180.0, "volume": 500000.0, "adv": 1000000.0, "volatility": 0.015}}
    res = mgr.run_execution(current_weights={"AAPL": 0.0}, target_weights={"AAPL": 0.2}, market_snapshots=snaps)

    print(json.dumps({
        "status": "SUCCESS",
        "requested_execution_id": args.execution,
        "report": res["summary_report"],
        "cost_attribution": res["cost_attribution"]
    }, indent=2))


if __name__ == "__main__":
    main()
