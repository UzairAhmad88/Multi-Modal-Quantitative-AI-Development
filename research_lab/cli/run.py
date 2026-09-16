"""
CLI tool for executing an experiment run.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research_lab.manager import ExperimentManager


def main():
    parser = argparse.ArgumentParser(description="Run Experiment")
    parser.add_argument("--experiment", type=str, default="EXP-001", help="Experiment ID")
    args = parser.parse_args()

    mgr = ExperimentManager()
    res = mgr.run_experiment(args.experiment)

    print(json.dumps({
        "status": "SUCCESS",
        "experiment_id": res["experiment_id"],
        "configuration_hash": res["configuration_hash"],
        "cagr": res["metrics"]["cagr"],
        "sharpe_ratio": res["metrics"]["sharpe_ratio"],
        "max_drawdown": res["metrics"]["max_drawdown"],
        "lineage_depth": res["lineage"]["depth"]
    }, indent=2))


if __name__ == "__main__":
    main()
