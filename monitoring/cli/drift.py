"""
CLI for running Data Drift audit between baseline and target files.
"""

import argparse
import numpy as np
import pandas as pd
from monitoring.data_drift.detector import DataDriftDetector


def main():
    parser = argparse.ArgumentParser(description="Standalone Data Drift Audit CLI")
    parser.add_argument("--baseline", type=str, required=False, help="Baseline CSV file path")
    parser.add_argument("--target", type=str, required=False, help="Target CSV file path")
    args = parser.parse_args()

    if args.baseline and args.target:
        b_df = pd.read_csv(args.baseline)
        t_df = pd.read_csv(args.target)
    else:
        np.random.seed(42)
        b_df = pd.DataFrame({"volatility": np.random.normal(0.01, 0.002, 100)})
        t_df = pd.DataFrame({"volatility": np.random.normal(0.02, 0.005, 100)})

    detector = DataDriftDetector()
    results = detector.evaluate_feature_drift(b_df, t_df)

    print("=== Data Drift Audit ===")
    for r in results:
        print(f"Feature '{r.feature_name}': PSI={r.psi_score:.4f}, KS p={r.ks_pvalue:.4e} -> {r.severity} ({'DRIFTED' if r.is_drifted else 'STABLE'})")


if __name__ == "__main__":
    main()
