"""
CLI for Inspecting Versioned Datasets.
Usage: python data_platform/cli/inspect.py --dataset DATASET-001
"""

import argparse
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def main():
    parser = argparse.ArgumentParser(description="Inspect dataset metadata and contents.")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset ID")

    args = parser.parse_args()
    datasets_dir = Path("data/datasets")
    meta_path = datasets_dir / f"{args.dataset}_meta.json"

    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        print(f"[DATASET METADATA] {json.dumps(meta, indent=2)}")
    else:
        print(f"[ERROR] Dataset metadata not found for ID: {args.dataset}")


if __name__ == "__main__":
    main()
