"""
CLI tool for running strategy evaluation and statistical validation.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research_evaluation.manager import ResearchEvaluationManager


def main():
    parser = argparse.ArgumentParser(description="Run Strategy Research Evaluation")
    parser.add_argument("--strategy", type=str, default="STRATEGY-001", help="Strategy ID")
    parser.add_argument("--config", type=str, default="configs/evaluation/default.yaml", help="Path to config YAML")
    args = parser.parse_args()

    mgr = ResearchEvaluationManager()
    res = mgr.evaluate_strategy(strategy_id=args.strategy)

    print(json.dumps({
        "status": "SUCCESS",
        "evaluation_id": res["evaluation_id"],
        "strategy_id": res["strategy_id"],
        "cagr": res["performance"]["cagr"],
        "sharpe_ratio": res["performance"]["sharpe_ratio"],
        "bootstrap_sharpe_ci": [res["bootstrap"]["ci_lower"], res["bootstrap"]["ci_upper"]],
        "walk_forward_oos_sharpe": res["walk_forward"]["out_of_sample_sharpe"],
        "robustness_score": res["robustness"]["robustness_score"],
        "overfitting_risk": res["overfitting"]["overfitting_risk_level"]
    }, indent=2))


if __name__ == "__main__":
    main()
