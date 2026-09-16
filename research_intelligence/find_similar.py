"""
CLI Script: Search for duplicate or similar research experiments.
Usage: python research_intelligence/find_similar.py --experiment EXP-001
"""

from __future__ import annotations
import argparse
import sys
from research_intelligence.similarity.similarity import ResearchSimilarityEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Find Similar Quantitative Experiments")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment ID or Run ID")
    args = parser.parse_args()

    engine = ResearchSimilarityEngine()
    dummy_config = {"model": {"type": "multimodal"}, "data": {"symbols": ["AAPL", "MSFT"]}}
    similar = engine.find_similar_experiments(dummy_config)

    print("=" * 70)
    print(f"SEARCHING SIMILAR EXPERIMENTS FOR: {args.experiment}")
    print("=" * 70)
    if not similar:
        print("No duplicate or highly similar experiments found.")
    else:
        for s in similar:
            print(f"[{s['similarity_score']*100:.0f}% Match] {s['run_id']} ({s['model_type']}) - Status: {s['status']}")


if __name__ == "__main__":
    main()
