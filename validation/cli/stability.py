"""
CLI Tool: Inspect Stability Results.
"""

import argparse
import json
from validation.core.validation_manager import StatisticalValidationManager


def main():
    parser = argparse.ArgumentParser(description="Inspect Stability Results")
    parser.add_argument("--validation", type=str, required=True, help="Validation ID")
    args = parser.parse_args()

    mgr = StatisticalValidationManager()
    val = mgr.get_validation(args.validation)
    if val and val.stability_result:
        print(json.dumps(val.stability_result.model_dump(), indent=2))


if __name__ == "__main__":
    main()
