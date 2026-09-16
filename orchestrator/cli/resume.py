"""
CLI tool: Resume Workflow.
"""

import argparse
from orchestrator.core.orchestrator import ResearchOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Resume Workflow")
    parser.add_argument("--workflow", type=str, required=True, help="Workflow ID")
    args = parser.parse_args()

    orchestrator = ResearchOrchestrator()
    wf = orchestrator.resume_workflow(args.workflow)
    print(f"Workflow '{wf.workflow_id}' resumed and finished with status: {wf.status.value}")


if __name__ == "__main__":
    main()
