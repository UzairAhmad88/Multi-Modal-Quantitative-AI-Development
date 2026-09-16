"""
CLI script: Resume a failed or paused quantitative research experiment from latest valid checkpoint.
Usage: python research/resume.py --run-id RUN-20260916-0001
"""

from __future__ import annotations
import argparse
import sys
from research.registry.registry import ExperimentRegistry
from orchestration.pipeline import ResearchPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Resume Research Experiment from Checkpoint")
    parser.add_argument("--run-id", type=str, required=True, help="Run ID to resume")
    args = parser.parse_args()

    registry = ExperimentRegistry()
    run = registry.get_run(args.run_id)

    if not run:
        print(f"Error: Run ID '{args.run_id}' not found in registry.", file=sys.stderr)
        sys.exit(1)

    config = run.get("config")
    if not config:
        print(f"Error: Configuration missing for run '{args.run_id}'.", file=sys.stderr)
        sys.exit(1)

    print(f"Resuming pipeline run '{args.run_id}' from latest checkpoint...")
    pipeline = ResearchPipeline(config=config, resume_run_id=args.run_id)
    run_record = pipeline.execute()

    print("\n--- Resumed Execution Summary ---")
    print(f"Run ID:    {run_record.get('run_id')}")
    print(f"Status:    {run_record.get('status')}")
    print(f"Completed: {run_record.get('completed_stages')}/{run_record.get('total_stages')} stages")


if __name__ == "__main__":
    main()
