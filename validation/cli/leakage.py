"""
CLI Command for Data Leakage Audits.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from validation.leakage.detector import LeakageDetector


def main():
    parser = argparse.ArgumentParser(description="Run Data Leakage Auditor.")
    parser.add_argument("--sample-size", type=int, default=300, help="Sample dataset size")
    args = parser.parse_args()

    print("🔍 Auditing Dataset for Data Leakage...")
    np.random.seed(42)
    dates = pd.date_range("2022-01-01", periods=args.sample_size, freq="B")
    df = pd.DataFrame({
        "timestamp": dates.strftime("%Y-%m-%d"),
        "availability_timestamp": (dates - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
        "feature_1": np.random.normal(0, 1, size=args.sample_size),
        "target": np.random.normal(0.0005, 0.012, size=args.sample_size),
    })

    audit = LeakageDetector.audit_full_dataset(df, decision_col="timestamp", target_col="target")

    print(f"\nAudit Status: {audit['status']}")
    print(f"Has Leakage:  {audit['has_leakage']}")
    print(f"Total Issues: {audit['total_issues']}")
    if audit["issues"]:
        for issue in audit["issues"]:
            print(f" - ⚠️ {issue}")


if __name__ == "__main__":
    main()
