"""
CLI tool: Workflow Status.
"""

import argparse
import json
from orchestrator.core.orchestrator import ResearchOrchestrator
from orchestrator.monitoring.workflow_monitor import WorkflowMonitor


def main():
    parser = argparse.ArgumentParser(description="Workflow Status")
    parser.add_argument("--workflow", type=str, required=True, help="Workflow ID")
    args = parser.parse_args()

    orchestrator = ResearchOrchestrator()
    wf = orchestrator.get_workflow(args.workflow)
    if not wf:
        print(f"Workflow '{args.workflow}' not found.")
        return

    progress = WorkflowMonitor.get_progress(wf)
    print(f"Workflow ID: {wf.workflow_id}")
    print(f"Name       : {wf.name}")
    print(f"Status     : {wf.status.value}")
    print(f"Progress   : {progress['percent_complete']}% ({progress['completed_tasks']}/{progress['total_tasks']} tasks)")
    print("\nTasks Breakdown:")
    for t in wf.tasks:
        print(f"  - [{t.status.value}] {t.task_id}: {t.name}")


if __name__ == "__main__":
    main()
