"""
CLI Tool: Search Knowledge Base.
"""

import argparse
import json
from knowledge.search.search_engine import KnowledgeSearchEngine


def main():
    parser = argparse.ArgumentParser(description="Search Research Knowledge Base")
    parser.add_argument("--query", type=str, help="Free-text semantic query")
    parser.add_argument("--model", type=str, help="Filter by model ID")
    parser.add_argument("--modality", type=str, help="Filter by modality")
    parser.add_argument("--dataset", type=str, help="Filter by dataset ID")
    parser.add_argument("--status", type=str, help="Filter by status (COMPLETED/FAILED)")
    parser.add_argument("--min-sharpe", type=float, help="Filter by minimum Sharpe ratio")
    args = parser.parse_args()

    engine = KnowledgeSearchEngine()
    results = engine.search(
        query=args.query,
        model=args.model,
        modality=args.modality,
        dataset=args.dataset,
        status=args.status,
        min_sharpe=args.min_sharpe,
    )

    print(f"Found {len(results)} matching research records:")
    for r in results:
        print(f"  - [{r['status']}] {r['experiment_id']} | Model: {r['model_id']} | Sharpe: {r['metrics'].get('sharpe_ratio', 'N/A')} (Relevance: {r.get('relevance_score', 1.0)})")


if __name__ == "__main__":
    main()
