"""
CLI Tool: Inspect Bootstrap Results.
"""

import argparse
import json
from validation.core.validation_manager import StatisticalValidationManager


def main():
    parser = argparse.ArgumentParser(description="Inspect Bootstrap Results")
    parser.add_argument("--validation", type=str, required=True, help="Validation ID")
    args = parser.parse_args()

    mgr = StatisticalValidationManager()
    val = mgr.get_validation(args.validation)
    if not val:
        print(f"Validation '{args.validation}' not found.")
        return

    print(json.dumps([b.model_dump() for b in val.bootstrap_results], indent=2))


if __name__ == "__main__":
    main()
