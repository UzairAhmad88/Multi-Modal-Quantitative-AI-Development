"""
CLI tool: Start workflow execution.
"""

import argparse
from orchestrator.core.orchestrator import ResearchOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Start Orchestrator Workflow")
    parser.add_argument("--workflow", type=str, required=True, help="Workflow ID")
    args = parser.parse_args()

    orchestrator = ResearchOrchestrator()
    wf = orchestrator.start_workflow(args.workflow)
    print(f"Workflow '{wf.workflow_id}' execution completed with status: {wf.status.value}")


if __name__ == "__main__":
    main()
