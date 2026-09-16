"""
CLI tool: Validate workflow.
"""

import argparse
from orchestrator.core.orchestrator import ResearchOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Validate Orchestrator Workflow")
    parser.add_argument("--workflow", type=str, required=True, help="Workflow ID")
    args = parser.parse_args()

    orchestrator = ResearchOrchestrator()
    results = orchestrator.validate_workflow(args.workflow)
    print(f"Validation completed for '{args.workflow}':")
    for r in results:
        print(f"  - [{r.status}] {r.policy}: {r.message}")


if __name__ == "__main__":
    main()
