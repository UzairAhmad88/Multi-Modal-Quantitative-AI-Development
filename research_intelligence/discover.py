"""
CLI Script: Run automated pattern discovery across dataset.
Usage: python research_intelligence/discover.py
"""

from __future__ import annotations
import json
from research_intelligence.engine import ResearchIntelligenceEngine


def main() -> None:
    print("=" * 70)
    print("RUNNING AUTOMATED QUANTITATIVE PATTERN DISCOVERY")
    print("=" * 70)

    engine = ResearchIntelligenceEngine()
    res = engine.discover_and_hypothesize()

    print(f"\nDiscovered {len(res['patterns'])} patterns and {len(res['anomalies'])} anomalies.")
    print(f"Generated {res['total_hypotheses']} testable research hypotheses.\n")

    print("-" * 70)
    print(f"{'Category':<15} {'Pattern Name':<30} {'Metric'}")
    print("-" * 70)
    for p in res['patterns']:
        cat = p.get('category', 'GENERAL')
        name = p.get('pattern_name', 'Pattern')[:28]
        val = p.get('metric_value', 'N/A')
        print(f"{cat:<15} {name:<30} {val}")
    print("-" * 70)

    if res['generated_hypotheses']:
        print("\nTop Generated Hypotheses:")
        for h in res['generated_hypotheses'][:3]:
            print(f"  [{h['hypothesis_id']}] {h['statement']}")


if __name__ == "__main__":
    main()
