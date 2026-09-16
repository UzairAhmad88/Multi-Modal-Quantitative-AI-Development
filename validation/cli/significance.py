"""
CLI Tool: Inspect Significance Results.
"""

import argparse
import json
from validation.core.validation_manager import StatisticalValidationManager


def main():
    parser = argparse.ArgumentParser(description="Inspect Significance Results")
    parser.add_argument("--validation", type=str, required=True, help="Validation ID")
    args = parser.parse_args()

    mgr = StatisticalValidationManager()
    val = mgr.get_validation(args.validation)
    if val:
        print(json.dumps([s.model_dump() for s in val.significance_results], indent=2))


if __name__ == "__main__":
    main()
