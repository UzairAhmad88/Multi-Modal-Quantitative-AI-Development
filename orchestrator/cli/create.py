"""
CLI tool: Create workflow.
"""

import argparse
import sys
from orchestrator.core.orchestrator import ResearchOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Create Orchestrator Workflow")
    parser.add_argument("--template", type=str, default="full_research", help="Workflow template name")
    parser.add_argument("--name", type=str, default="Multimodal Quant Research Workflow", help="Workflow name")
    args = parser.parse_args()

    orchestrator = ResearchOrchestrator()
    wf = orchestrator.create_workflow(name=args.name, template=args.template)
    print(f"Workflow created successfully: {wf.workflow_id} (Status: {wf.status.value})")


if __name__ == "__main__":
    main()
