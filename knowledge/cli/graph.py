"""
CLI Tool: Knowledge Graph Export & Query.
"""

import json
from knowledge.repository.knowledge_repository import KnowledgeRepository
from knowledge.graph.knowledge_graph import ResearchKnowledgeGraph


def main():
    repo = KnowledgeRepository()
    records = repo.list_records()
    kg = ResearchKnowledgeGraph()
    kg.build_from_records(records)
    print(json.dumps(kg.to_dict(), indent=2))


if __name__ == "__main__":
    main()
