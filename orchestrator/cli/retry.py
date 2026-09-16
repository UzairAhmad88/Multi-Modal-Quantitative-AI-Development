"""
CLI tool: Retry Workflow.
"""

import argparse
from orchestrator.core.orchestrator import ResearchOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Retry Workflow")
    parser.add_argument("--workflow", type=str, required=True, help="Workflow ID")
    args = parser.parse_args()

    orchestrator = ResearchOrchestrator()
    wf = orchestrator.retry_workflow(args.workflow)
    print(f"Workflow '{wf.workflow_id}' retried and completed (Status: {wf.status.value})")


if __name__ == "__main__":
    main()
