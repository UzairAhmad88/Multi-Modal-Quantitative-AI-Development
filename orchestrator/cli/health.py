"""
CLI tool: Orchestrator Health Check.
"""

import json
from orchestrator.core.orchestrator import ResearchOrchestrator


def main():
    orchestrator = ResearchOrchestrator()
    health = orchestrator.get_health()
    print(json.dumps(health, indent=2))


if __name__ == "__main__":
    main()
