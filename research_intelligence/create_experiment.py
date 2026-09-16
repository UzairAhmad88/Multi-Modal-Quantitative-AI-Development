"""
CLI Script: Convert a research hypothesis into an executable experiment YAML configuration.
Usage: python research_intelligence/create_experiment.py --hypothesis HYP-20260916-0001
"""

from __future__ import annotations
import argparse
import sys
from research_intelligence.engine import ResearchIntelligenceEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Experiment Config from Hypothesis")
    parser.add_argument("--hypothesis", type=str, required=True, help="Hypothesis ID (HYP-xxxx)")
    parser.add_argument("--model", type=str, default="multimodal", help="Model type (multimodal, lstm, etc.)")
    args = parser.parse_args()

    engine = ResearchIntelligenceEngine()
    try:
        res = engine.generate_experiment_config_for_hypothesis = engine.generate_experiment_for_hypothesis(
            hypothesis_id=args.hypothesis,
            model_type=args.model
        )
        print("=" * 70)
        print(f"EXPERIMENT CREATED FOR HYPOTHESIS: {args.hypothesis}")
        print("=" * 70)
        print(f"Experiment ID:    {res['experiment_id']}")
        print(f"Config YAML Path: {res['config_yaml_path']}")
        if res.get("similar_experiments"):
            print("\nWarning: Similar existing experiments found:")
            for s in res["similar_experiments"][:2]:
                print(f"  - {s['warning']}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
