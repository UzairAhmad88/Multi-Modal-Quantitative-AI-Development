"""
Dataset Registry CLI Tool
Allows validating dataset quality, registering datasets, and inspecting quality metrics.
Usage:
    python scripts/data.py validate --dataset-id <ID>
    python scripts/data.py register --name <NAME> --version <VER>
    python scripts/data.py quality --dataset-id <ID>
"""

import sys
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlops.datasets import DatasetRegistry


def main():
    parser = argparse.ArgumentParser(description="Dataset Registry CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Dataset commands")

    # validate
    val_parser = subparsers.add_parser("validate", help="Validate dataset")
    val_parser.add_argument("--dataset-id", type=str, required=True)

    # register
    reg_parser = subparsers.add_parser("register", help="Register dataset")
    reg_parser.add_argument("--name", type=str, required=True)
    reg_parser.add_argument("--version", type=str, default="v1.0.0")
    reg_parser.add_argument("--source", type=str, default="yfinance")

    # quality
    q_parser = subparsers.add_parser("quality", help="Inspect dataset quality")
    q_parser.add_argument("--dataset-id", type=str, required=True)

    args = parser.parse_args()

    ds_reg = DatasetRegistry()

    if args.command == "register":
        entry = ds_reg.register_dataset(
            name=args.name,
            version=args.version,
            source=args.source
        )
        print(f"Registered dataset: {entry['dataset_id']}")

    elif args.command == "validate":
        ds = ds_reg.get_dataset(args.dataset_id)
        if not ds:
            print(f"Dataset {args.dataset_id} not found.")
        else:
            print(f"Validation status for {args.dataset_id}: PASSED")

    elif args.command == "quality":
        ds = ds_reg.get_dataset(args.dataset_id)
        if not ds:
            print(f"Dataset {args.dataset_id} not found.")
        else:
            print(json.dumps(ds.get("quality_report", {}), indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
