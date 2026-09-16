"""
CLI tool for replicating an experiment.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research_lab.manager import ExperimentManager


def main():
    parser = argparse.ArgumentParser(description="Replicate Experiment")
    parser.add_argument("--experiment", type=str, default="EXP-001", help="Experiment ID to replicate")
    args = parser.parse_args()

    mgr = ExperimentManager()
    res = mgr.replicate_experiment(args.experiment)

    print(json.dumps({
        "status": "SUCCESS",
        "original_experiment_id": res["original_experiment_id"],
        "replication_experiment_id": res["replication_experiment_id"],
        "reproducibility_status": res["reproducibility_status"],
        "details": res["details"]
    }, indent=2))


if __name__ == "__main__":
    main()
