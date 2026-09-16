"""
CLI for Data Validation.
Usage: python data_platform/cli/validate.py --dataset DATASET-001
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data_platform.manager import DataPlatformManager


def main():
    parser = argparse.ArgumentParser(description="Validate data platform dataset quality.")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset ID or filepath")

    args = parser.parse_args()
    mgr = DataPlatformManager()

    filepath = Path("data/datasets") / f"{args.dataset}.parquet"
    if not filepath.exists():
        filepath = Path(args.dataset)

    if filepath.exists():
        df = pd.read_parquet(filepath)
        res = mgr.quality_engine.validate_dataset(df, dataset_id=args.dataset)
        print(f"[DATA QUALITY REPORT] {res}")
    else:
        print(f"[ERROR] Dataset file not found: {filepath}")


if __name__ == "__main__":
    main()
