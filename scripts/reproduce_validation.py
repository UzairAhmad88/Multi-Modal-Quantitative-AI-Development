"""
Reproduce Validation Script.
Usage:
    python scripts/reproduce_validation.py --experiment-id EXP-2026-000001
"""

import sys
from pathlib import Path
import argparse
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.orchestrator import ValidationPipeline


def main():
    parser = argparse.ArgumentParser(description="Reproduce Strategy Validation Run")
    parser.add_argument("--experiment-id", required=True, help="Experiment ID to reproduce")
    args = parser.parse_args()

    pipeline = ValidationPipeline()
    res = pipeline.run_full_validation_suite(args.experiment_id)

    print(f"Validation Reproduction Completed for {args.experiment_id}:")
    print(f"Validation Hash: {res['reproducibility']['validation_hash']}")
    print(json.dumps(res["validation_summary"], indent=2))


if __name__ == "__main__":
    main()
