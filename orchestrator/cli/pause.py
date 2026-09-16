"""
CLI tools: Pause, Cancel, and Retry Workflow.
"""

import argparse
from orchestrator.core.orchestrator import ResearchOrchestrator


def main_pause():
    parser = argparse.ArgumentParser(description="Pause Workflow")
    parser.add_argument("--workflow", type=str, required=True, help="Workflow ID")
    args = parser.parse_args()
    orchestrator = ResearchOrchestrator()
    wf = orchestrator.pause_workflow(args.workflow)
    print(f"Workflow '{wf.workflow_id}' paused (Status: {wf.status.value})")


def main_cancel():
    parser = argparse.ArgumentParser(description="Cancel Workflow")
    parser.add_argument("--workflow", type=str, required=True, help="Workflow ID")
    args = parser.parse_args()
    orchestrator = ResearchOrchestrator()
    wf = orchestrator.cancel_workflow(args.workflow)
    print(f"Workflow '{wf.workflow_id}' cancelled (Status: {wf.status.value})")


def main_retry():
    parser = argparse.ArgumentParser(description="Retry Workflow")
    parser.add_argument("--workflow", type=str, required=True, help="Workflow ID")
    args = parser.parse_args()
    orchestrator = ResearchOrchestrator()
    wf = orchestrator.retry_workflow(args.workflow)
    print(f"Workflow '{wf.workflow_id}' retried and completed (Status: {wf.status.value})")


if __name__ == "__main__":
    main_pause()
