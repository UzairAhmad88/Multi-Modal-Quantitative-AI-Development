"""
CLI Tool: Compare Experiments.
"""

import argparse
import json
from knowledge.comparison.comparison_engine import ExperimentComparisonEngine


def main():
    parser = argparse.ArgumentParser(description="Compare Research Experiments")
    parser.add_argument("exp_a", type=str, help="First Experiment ID")
    parser.add_argument("exp_b", type=str, help="Second Experiment ID")
    args = parser.parse_args()

    engine = ExperimentComparisonEngine()
    try:
        comp = engine.compare_experiments(args.exp_a, args.exp_b)
        print(json.dumps(comp, indent=2))
    except ValueError as e:
        print(f"Comparison Error: {e}")


if __name__ == "__main__":
    main()
