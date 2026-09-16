"""
CLI Script: Display details of a structured research hypothesis.
Usage: python research_intelligence/show_hypothesis.py --id HYP-20260916-0001
"""

from __future__ import annotations
import argparse
import sys
import yaml
from research_intelligence.hypotheses.hypothesis_engine import HypothesisEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Show Research Hypothesis Details")
    parser.add_argument("--id", type=str, required=True, help="Hypothesis ID (HYP-xxxx)")
    args = parser.parse_args()

    he = HypothesisEngine()
    hyp = he.get_hypothesis(args.id)

    if not hyp:
        print(f"Error: Hypothesis ID '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print(f"RESEARCH HYPOTHESIS: {hyp.hypothesis_id}")
    print("=" * 70)
    print(hyp.to_yaml())


if __name__ == "__main__":
    main()
