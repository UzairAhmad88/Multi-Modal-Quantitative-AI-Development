"""
CLI tool: Cancel Workflow.
"""

import argparse
from orchestrator.core.orchestrator import ResearchOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Cancel Workflow")
    parser.add_argument("--workflow", type=str, required=True, help="Workflow ID")
    args = parser.parse_args()

    orchestrator = ResearchOrchestrator()
    wf = orchestrator.cancel_workflow(args.workflow)
    print(f"Workflow '{wf.workflow_id}' cancelled (Status: {wf.status.value})")


if __name__ == "__main__":
    main()
