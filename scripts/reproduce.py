"""
Quantitative Experiment Reproduction CLI Engine
Reproduces an existing experiment run deterministically using stored configs and manifests.
Usage:
    python scripts/reproduce.py --run-id <RUN_ID>
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlops.reproducer import ExperimentReproducer


def main():
    parser = argparse.ArgumentParser(description="Reproduce quantitative experiment run")
    parser.add_argument("--run-id", type=str, required=True, help="Run ID of the experiment to reproduce")
    args = parser.parse_args()

    reproducer = ExperimentReproducer()
    print(f"[MLOps Reproducer] Attempting reproduction of run: {args.run_id}")
    res = reproducer.reproduce(args.run_id)

    print("\n" + "=" * 60)
    print("EXPERIMENT REPRODUCTION REPORT")
    print("=" * 60)
    print(f"Original Run ID:   {res.get('original_run_id')}")
    print(f"Reproduction ID:   {res.get('reproduction_run_id')}")
    print(f"Match Status:      {res.get('match_status')}")
    print(f"Environment Diff:  {res.get('environment_diff')}")
    print(f"Metrics Diff:      {res.get('metrics_diff')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
