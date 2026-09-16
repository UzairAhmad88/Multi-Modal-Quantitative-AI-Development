"""
CLI tool for inspecting strategy robustness testing results.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research_evaluation.manager import ResearchEvaluationManager


def main():
    parser = argparse.ArgumentParser(description="Run Robustness Analysis")
    parser.add_argument("--evaluation", type=str, default="EVAL-LATEST", help="Evaluation ID")
    args = parser.parse_args()

    mgr = ResearchEvaluationManager()
    res = mgr.evaluate_strategy()

    print(json.dumps({
        "status": "SUCCESS",
        "evaluation_id": res["evaluation_id"],
        "robustness": res["robustness"]
    }, indent=2))


if __name__ == "__main__":
    main()
