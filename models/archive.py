"""
CLI Script: Archive quantitative model version.
Usage: python models/archive.py --id MODEL-20260916-0001
"""

from __future__ import annotations
import argparse
import sys
from models.registry.registry import ModelRegistry, ModelStatus


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive Quantitative Model")
    parser.add_argument("--id", type=str, required=True, help="Model ID")
    args = parser.parse_args()

    registry = ModelRegistry()
    success = registry.update_model_status(args.id, ModelStatus.ARCHIVED)

    if success:
        print(f"Successfully marked model '{args.id}' as ARCHIVED.")
    else:
        print(f"Error: Model '{args.id}' not found in registry.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
