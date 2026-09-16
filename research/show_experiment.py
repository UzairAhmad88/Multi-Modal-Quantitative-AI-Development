"""
CLI script: Display detailed configuration, metrics, and artifact status of an experiment or run.
Usage: python research/show_experiment.py --id EXP-20260916-0001 (or RUN-20260916-0001)
"""

from __future__ import annotations
import argparse
import json
import sys
from research.registry.registry import ExperimentRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="Show Quantitative Experiment Details")
    parser.add_argument("--id", type=str, required=True, help="Experiment ID (EXP-xxxx) or Run ID (RUN-xxxx)")
    args = parser.parse_args()

    registry = ExperimentRegistry()
    target_id = args.id

    if target_id.startswith("EXP-"):
        exp = registry.get_experiment(target_id)
        if not exp:
            print(f"Experiment ID '{target_id}' not found in registry.", file=sys.stderr)
            sys.exit(1)
        print("=" * 60)
        print(f"EXPERIMENT: {exp.get('experiment_id')}")
        print(f"Name:       {exp.get('name')}")
        print(f"Status:     {exp.get('status')}")
        print(f"Tags:       {', '.join(exp.get('tags', []))}")
        print(f"Notes:      {exp.get('notes')}")
        print(f"Runs:       {len(exp.get('runs', []))}")
        print("=" * 60)
        print("\nConfiguration:")
        print(json.dumps(exp.get("config", {}), indent=2))

    else:
        run = registry.get_run(target_id)
        if not run:
            print(f"Run ID '{target_id}' not found in registry.", file=sys.stderr)
            sys.exit(1)
        print("=" * 60)
        print(f"RUN ID:        {run.get('run_id')}")
        print(f"Experiment ID: {run.get('experiment_id')}")
        print(f"Status:        {run.get('status')}")
        print(f"Timestamp:     {run.get('timestamp')}")
        print("=" * 60)
        print("\nMetrics:")
        print(json.dumps(run.get("metrics", {}), indent=2))
        print("\nArtifacts:")
        print(json.dumps(run.get("artifacts", {}), indent=2))
        if run.get("error"):
            print(f"\nError: {run.get('error')}")


if __name__ == "__main__":
    main()
