"""
CLI Tool: Inspect Statistical Validation.
"""

import argparse
import json
from validation.core.validation_manager import StatisticalValidationManager


def main():
    parser = argparse.ArgumentParser(description="Inspect Statistical Validation")
    parser.add_argument("--validation", type=str, required=True, help="Validation ID or Experiment ID")
    args = parser.parse_args()

    mgr = StatisticalValidationManager()
    val = mgr.get_validation(args.validation)
    if not val:
        print(f"Validation '{args.validation}' not found.")
        return

    print(json.dumps(val.model_dump(), indent=2))


if __name__ == "__main__":
    main()
