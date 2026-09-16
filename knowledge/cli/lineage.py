"""
CLI Tool: Trace Experiment Lineage.
"""

import argparse
import json
from knowledge.repository.knowledge_repository import KnowledgeRepository
from knowledge.lineage.lineage_service import ResearchLineageService


def main():
    parser = argparse.ArgumentParser(description="Trace Experiment Lineage")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment ID")
    args = parser.parse_args()

    repo = KnowledgeRepository()
    record = repo.get_record(args.experiment)
    if not record:
        print(f"Record '{args.experiment}' not found.")
        return

    lineage = ResearchLineageService.get_experiment_lineage(record)
    print(json.dumps(lineage, indent=2))


if __name__ == "__main__":
    main()
