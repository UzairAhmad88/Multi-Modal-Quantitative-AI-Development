"""
CLI Tool: Inspect Multiple Testing Adjustments.
"""

import argparse
import json
from validation.core.validation_manager import StatisticalValidationManager


def main():
    parser = argparse.ArgumentParser(description="Inspect Multiple Testing Results")
    parser.add_argument("--validation", type=str, required=True, help="Validation ID")
    args = parser.parse_args()

    mgr = StatisticalValidationManager()
    val = mgr.get_validation(args.validation)
    if val and val.multiple_testing_result:
        print(json.dumps(val.multiple_testing_result.model_dump(), indent=2))


if __name__ == "__main__":
    main()
