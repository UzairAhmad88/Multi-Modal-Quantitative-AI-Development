"""
CLI Tool: Inspect Knowledge Record.
"""

import argparse
import json
from knowledge.repository.knowledge_repository import KnowledgeRepository


def main():
    parser = argparse.ArgumentParser(description="Inspect Knowledge Record")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment or Knowledge ID")
    args = parser.parse_args()

    repo = KnowledgeRepository()
    record = repo.get_record(args.experiment)
    if not record:
        print(f"Record '{args.experiment}' not found.")
        return

    print(json.dumps(record.model_dump(), indent=2))


if __name__ == "__main__":
    main()
