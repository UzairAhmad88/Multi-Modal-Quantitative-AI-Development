"""
Data Quality Engine for Validating Schemas, Sanity Checks, Null Ratios, and Price Anomalies.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import json
import datetime
from typing import Dict, Any, List, Optional


class DataQualityEngine:
    """Executes quality rules and outputs data quality audit reports."""

    def __init__(self, reports_dir: str = "reports/data_quality"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def validate_market(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validates market price data against quality gates."""
        if df.empty:
            return {"status": "FAIL", "reason": "Empty market dataframe"}

        issues = []
        checks = {}

        # 1. Null ratio check
        null_ratio = df[["open", "high", "low", "close"]].isnull().mean().max() if set(["open", "high", "low", "close"]).issubset(df.columns) else 1.0
        checks["null_ratio"] = round(float(null_ratio), 4)
        if null_ratio > 0.05:
            issues.append(f"Null ratio {null_ratio:.1%} exceeds 5% threshold")

        # 2. Price sanity check (high >= low, high >= open, high >= close, low <= open, low <= close)
        if set(["open", "high", "low", "close"]).issubset(df.columns):
            invalid_high_low = (df["high"] < df["low"]).sum()
            invalid_price_range = ((df["high"] < df["open"]) | (df["high"] < df["close"]) | (df["low"] > df["open"]) | (df["low"] > df["close"])).sum()
            checks["invalid_high_low_count"] = int(invalid_high_low)
            checks["invalid_price_range_count"] = int(invalid_price_range)
            if invalid_high_low > 0 or invalid_price_range > 0:
                issues.append(f"Found {invalid_high_low + invalid_price_range} price sanity violations (high < low or range breach)")

        # 3. Non-negative prices & volume
        if "close" in df.columns:
            negative_prices = (df["close"] <= 0).sum()
            checks["negative_price_count"] = int(negative_prices)
            if negative_prices > 0:
                issues.append(f"Found {negative_prices} non-positive close prices")

        if "volume" in df.columns:
            negative_volume = (df["volume"] < 0).sum()
            checks["negative_volume_count"] = int(negative_volume)
            if negative_volume > 0:
                issues.append(f"Found {negative_volume} negative volume entries")

        # 4. Duplicate timestamps
        if {"symbol", "date"}.issubset(df.columns):
            dups = df.duplicated(subset=["symbol", "date"]).sum()
            checks["duplicate_records"] = int(dups)
            if dups > 0:
                issues.append(f"Found {dups} duplicate (symbol, date) records")

        status = "PASS" if not issues else ("WARNING" if len(issues) == 1 and null_ratio < 0.05 else "FAIL")
        res = {
            "status": status,
            "row_count": len(df),
            "symbol_count": df["symbol"].nunique() if "symbol" in df.columns else 0,
            "issues": issues,
            "checks": checks,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        self._save_report("market_quality.json", res)
        return res

    def validate_dataset(self, df: pd.DataFrame, dataset_id: str = "dataset") -> Dict[str, Any]:
        """Validates general compiled feature/dataset table."""
        if df.empty:
            return {"status": "FAIL", "reason": "Empty dataset"}

        null_ratio = float(df.isnull().mean().mean())
        dup_rows = int(df.duplicated().sum())

        status = "PASS" if null_ratio < 0.05 and dup_rows == 0 else ("WARNING" if null_ratio < 0.15 else "FAIL")
        res = {
            "dataset_id": dataset_id,
            "status": status,
            "rows": len(df),
            "columns": len(df.columns),
            "null_ratio": round(null_ratio, 4),
            "duplicate_rows": dup_rows,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        self._save_report(f"quality_{dataset_id}.json", res)
        return res

    def _save_report(self, filename: str, report: Dict[str, Any]) -> None:
        filepath = self.reports_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
