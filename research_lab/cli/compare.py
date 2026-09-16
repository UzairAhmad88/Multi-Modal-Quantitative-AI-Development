"""
CLI tool for comparing multiple experiments.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research_lab.manager import ExperimentManager


def main():
    parser = argparse.ArgumentParser(description="Compare Experiments")
    parser.add_argument("--experiments", type=str, default="EXP-001,EXP-002", help="Comma-separated experiment IDs")
    args = parser.parse_args()

    mgr = ExperimentManager()
    e_ids = [e.strip() for e in args.experiments.split(",")]
    res = mgr.compare_experiments(e_ids)

    print(json.dumps({
        "status": "SUCCESS",
        "experiments_compared": e_ids,
        "is_fair_comparison": res["is_fair_comparison"],
        "comparison_matrix": res["comparison_matrix"]
    }, indent=2))


if __name__ == "__main__":
    main()
