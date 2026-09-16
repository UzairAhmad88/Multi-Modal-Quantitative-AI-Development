"""
CLI Script: Generate testable quantitative hypotheses.
Usage: python research_intelligence/generate_hypotheses.py
"""

from __future__ import annotations
import json
from research_intelligence.engine import ResearchIntelligenceEngine


def main() -> None:
    print("=" * 70)
    print("HYPOTHESIS GENERATION ENGINE")
    print("=" * 70)

    engine = ResearchIntelligenceEngine()
    res = engine.discover_and_hypothesize()

    hyps = res.get("generated_hypotheses", [])
    print(f"\nGenerated {len(hyps)} testable hypotheses:\n")
    print("-" * 80)
    print(f"{'Hypothesis ID':<20} {'Type':<15} {'Statement'}")
    print("-" * 80)
    for h in hyps:
        h_id = h.get("hypothesis_id", "N/A")
        h_type = h.get("hypothesis_type", "N/A")
        stmt = h.get("statement", "")[:45]
        print(f"{h_id:<20} {h_type:<15} {stmt}")
    print("-" * 80)


if __name__ == "__main__":
    main()
