"""
CLI tool for running walk-forward validation across expanding/rolling time windows.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research_evaluation.manager import ResearchEvaluationManager


def main():
    parser = argparse.ArgumentParser(description="Run Walk-Forward Evaluation")
    parser.add_argument("--strategy", type=str, default="STRATEGY-001", help="Strategy ID")
    parser.add_argument("--config", type=str, default="configs/evaluation/walk_forward.yaml", help="Path to config YAML")
    args = parser.parse_args()

    mgr = ResearchEvaluationManager()
    res = mgr.evaluate_strategy(strategy_id=args.strategy)

    print(json.dumps({
        "status": "SUCCESS",
        "strategy_id": args.strategy,
        "evaluation_id": res["evaluation_id"],
        "walk_forward_summary": res["walk_forward"]
    }, indent=2))


if __name__ == "__main__":
    main()
