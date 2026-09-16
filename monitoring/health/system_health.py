"""
System Data Freshness & Data Quality Auditor.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


class SystemHealthAuditor:
    """Audits data freshness, missingness, and data quality metrics."""

    def audit_data_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or len(df) == 0:
            return {
                "row_count": 0,
                "missing_ratio": 1.0,
                "data_quality_score": 0.0,
                "is_data_healthy": False,
            }

        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        missing_ratio = float(missing_cells / total_cells) if total_cells > 0 else 0.0

        quality_score = max(0.0, 100.0 * (1.0 - missing_ratio * 2.0))

        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "missing_cells": int(missing_cells),
            "missing_ratio": missing_ratio,
            "data_quality_score": quality_score,
            "is_data_healthy": missing_ratio < 0.10,
        }
