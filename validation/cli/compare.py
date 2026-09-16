"""
CLI Tool: Compare Statistical Validations.
"""

import argparse
import json
from validation.core.validation_manager import StatisticalValidationManager


def main():
    parser = argparse.ArgumentParser(description="Compare Statistical Validations")
    parser.add_argument("val_a", type=str, help="First Validation ID")
    parser.add_argument("val_b", type=str, help="Second Validation ID")
    args = parser.parse_args()

    mgr = StatisticalValidationManager()
    val_a = mgr.get_validation(args.val_a)
    val_b = mgr.get_validation(args.val_b)

    if not val_a or not val_b:
        print("One or both validation records not found.")
        return

    comp = {
        "validation_a": val_a.validation_id,
        "validation_b": val_b.validation_id,
        "mean_a": val_a.basic_statistics.get("mean"),
        "mean_b": val_b.basic_statistics.get("mean"),
        "sample_a": val_a.sample_size,
        "sample_b": val_b.sample_size,
        "stability_a": val_a.stability_result.stability_score if val_a.stability_result else None,
        "stability_b": val_b.stability_result.stability_score if val_b.stability_result else None,
    }
    print(json.dumps(comp, indent=2))


if __name__ == "__main__":
    main()
