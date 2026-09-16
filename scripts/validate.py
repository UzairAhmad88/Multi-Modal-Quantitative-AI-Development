"""
CLI Validation Tool for Research-Grade Validation (Phase 13).
Usage:
    python scripts/validate.py --experiment-id EXP-2026-000001
    python scripts/validate.py --leakage --experiment-id EXP-2026-000001
    python scripts/validate.py --walk-forward --experiment-id EXP-2026-000001
    python scripts/validate.py --stress --experiment-id EXP-2026-000001
    python scripts/validate.py --statistics --experiment-id EXP-2026-000001
    python scripts/validate.py --robustness --experiment-id EXP-2026-000001
"""

import sys
from pathlib import Path
import argparse
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validation.orchestrator import ValidationPipeline

_pipeline = ValidationPipeline()


def main():
    parser = argparse.ArgumentParser(description="Multi-Modal Quant AI - Validation CLI")
    parser.add_argument("--experiment-id", required=True, help="Target experiment ID")
    parser.add_argument("--leakage", action="store_true", help="Run leakage audit only")
    parser.add_argument("--walk-forward", action="store_true", help="Run walk-forward CV only")
    parser.add_argument("--stress", action="store_true", help="Run stress test suite only")
    parser.add_argument("--statistics", action="store_true", help="Run statistical tests & CIs only")
    parser.add_argument("--robustness", action="store_true", help="Run parameter sweeps only")
    parser.add_argument("--reproduce", action="store_true", help="Audit validation reproducibility hash")

    args = parser.parse_args()

    suite = _pipeline.run_full_validation_suite(args.experiment_id)

    if args.leakage:
        print(json.dumps(suite["leakage_detection"], indent=2))
    elif args.walk_forward:
        print(json.dumps(suite["walk_forward"], indent=2))
    elif args.stress:
        print(json.dumps(suite["stress_testing"], indent=2))
    elif args.statistics:
        out = {
            "statistical_tests": suite["statistical_tests"],
            "bootstrap": suite["bootstrap"],
            "monte_carlo": suite["monte_carlo"],
        }
        print(json.dumps(out, indent=2))
    elif args.robustness:
        print(json.dumps(suite["sensitivity"], indent=2))
    elif args.reproduce:
        print(json.dumps(suite["reproducibility"], indent=2))
    else:
        print(json.dumps(suite["validation_summary"], indent=2))


if __name__ == "__main__":
    main()
