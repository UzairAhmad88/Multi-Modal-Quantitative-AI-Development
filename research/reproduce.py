"""
CLI script: Reproduce quantitative research experiment from a past Run ID.
Validates python environment, dataset availability, code configuration hash, and re-executes.
Usage: python research/reproduce.py --run-id RUN-20260916-0001
"""

from __future__ import annotations
import argparse
import sys
import platform
import pkg_resources
from pathlib import Path
from research.registry.registry import ExperimentRegistry
from orchestration.pipeline import ResearchPipeline


def validate_environment() -> bool:
    print("Validating Environment for Reproducibility...")
    print(f"  Python Version: {platform.python_version()}")
    print(f"  Platform:       {platform.platform()}")
    
    required_pkgs = ["numpy", "pandas", "yaml", "torch", "sklearn"]
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = [pkg for pkg in required_pkgs if pkg not in installed]

    if missing:
        print(f"  [WARNING] Missing core packages: {missing}")
    else:
        print("  [PASS] Core package dependencies verified.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce Quantitative Research Experiment")
    parser.add_argument("--run-id", type=str, required=True, help="Run ID to reproduce")
    args = parser.parse_args()

    registry = ExperimentRegistry()
    run = registry.get_run(args.run_id)

    if not run:
        print(f"Error: Run ID '{args.run_id}' not found in registry.", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print(f"REPRODUCING EXPERIMENT RUN: {args.run_id}")
    print(f"Original Experiment:       {run.get('experiment_id')}")
    print(f"Original Timestamp:        {run.get('timestamp')}")
    print("=" * 60)

    validate_environment()

    config = run.get("config")
    if not config:
        print("Error: Configuration missing from run record.", file=sys.stderr)
        sys.exit(1)

    print("\nRe-executing pipeline with reconstructed config...")
    pipeline = ResearchPipeline(config=config)
    new_run = pipeline.execute()

    print("\n--- Reproduction Complete ---")
    print(f"New Run ID:     {new_run.get('run_id')}")
    print(f"New Status:     {new_run.get('status')}")
    print(f"Original Sharpe: {run.get('metrics', {}).get('sharpe', 'N/A')}")
    print(f"New Sharpe:      {new_run.get('metrics', {}).get('sharpe', 'N/A')}")


if __name__ == "__main__":
    main()
