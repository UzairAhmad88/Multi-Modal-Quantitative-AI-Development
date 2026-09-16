"""
CLI script: Cancel a running quantitative research experiment pipeline.
Usage: python research/cancel.py --run-id RUN-20260916-0001
"""

from __future__ import annotations
import argparse
import sys
from research.registry.registry import ExperimentRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="Cancel Running Research Experiment")
    parser.add_argument("--run-id", type=str, required=True, help="Run ID to cancel")
    args = parser.parse_args()

    registry = ExperimentRegistry()
    run = registry.get_run(args.run_id)

    if not run:
        print(f"Error: Run ID '{args.run_id}' not found in registry.", file=sys.stderr)
        sys.exit(1)

    status = run.get("status")
    if status in ["COMPLETED", "FAILED", "CANCELLED"]:
        print(f"Run '{args.run_id}' is already in terminal state '{status}'. Cannot cancel.")
        sys.exit(0)

    registry.update_run_status(args.run_id, status="CANCELLED", error="Cancelled by user via CLI")
    print(f"Successfully marked run '{args.run_id}' as CANCELLED.")


if __name__ == "__main__":
    main()
