#!/usr/bin/env python3
"""
QUANT AI: Feature Quality Audit & CSV Report Generator
"""
from pathlib import Path
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.market_loader import load_market_data
from src.data.news_loader import load_news_data
from src.data.fundamental_loader import load_fundamentals
from src.data.data_synchronizer import align_modalities
from src.features.feature_fusion import FeatureBuilder
from src.utils.paths import REPORTS_DIR, ROOT

def generate_feature_quality_report():
    market_df = load_market_data("AAPL")
    news_df = load_news_data()
    fund_df = load_fundamentals()

    synced_df = align_modalities(market_df, news_df, fund_df)
    builder = FeatureBuilder()
    df, manifest = builder.build_dataset(synced_df)

    feature_cols = manifest["feature_names"]
    records = []

    for col in feature_cols:
        series = df[col]
        missing_pct = float(series.isnull().mean() * 100.0)
        unique_vals = int(series.nunique())
        mean_val = float(series.mean()) if pd.api.types.is_numeric_dtype(series) else 0.0
        std_val = float(series.std()) if pd.api.types.is_numeric_dtype(series) else 0.0
        min_val = float(series.min()) if pd.api.types.is_numeric_dtype(series) else 0.0
        max_val = float(series.max()) if pd.api.types.is_numeric_dtype(series) else 0.0
        inf_count = int(np.isinf(series).sum()) if pd.api.types.is_numeric_dtype(series) else 0

        flag = "OK"
        if missing_pct > 20.0:
            flag = "HIGH_MISSINGNESS"
        elif unique_vals <= 1:
            flag = "CONSTANT"
        elif inf_count > 0:
            flag = "INFINITE"

        records.append({
            "feature": col,
            "dtype": str(series.dtype),
            "missing_percentage": round(missing_pct, 2),
            "unique_values": unique_vals,
            "mean": round(mean_val, 4),
            "std": round(std_val, 4),
            "min": round(min_val, 4),
            "max": round(max_val, 4),
            "inf_count": inf_count,
            "status_flag": flag
        })

    report_df = pd.DataFrame(records)
    out_dir = Path(REPORTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "feature_quality.csv"
    report_df.to_csv(csv_path, index=False)
    print(f"Generated Feature Quality Report at: {csv_path} ({len(report_df)} features audited).")
    return csv_path

if __name__ == "__main__":
    generate_feature_quality_report()
