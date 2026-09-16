"""
CLI Tool: List Failed Experiments.
"""

import argparse
from knowledge.search.search_engine import KnowledgeSearchEngine


def main():
    engine = KnowledgeSearchEngine()
    failures = engine.search(status="FAILED")
    print(f"Found {len(failures)} failed experiment records:")
    for f in failures:
        details = f.get("failure_details", {}) or {}
        print(f"  - [{f['experiment_id']}] Model: {f['model_id']} | Reason: {details.get('error', 'Unknown failure')}")


if __name__ == "__main__":
    main()
