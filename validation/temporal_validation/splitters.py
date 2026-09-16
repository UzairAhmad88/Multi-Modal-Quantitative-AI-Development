"""
Temporal Splitters for Financial Time Series.
Provides chronological Train/Validation/Test splits with purging and embargo support.
"""

from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np


class TemporalSplitter:
    """Chronological time-series splitter respecting temporal order, purging, and embargo periods."""

    @staticmethod
    def chronological_split(
        df: pd.DataFrame,
        train_ratio: float = 0.6,
        val_ratio: float = 0.2,
        purge_window: int = 5,
        embargo_window: int = 5,
    ) -> Dict[str, Any]:
        """Splits DataFrame sequentially into Train, Validation, and Test sets with optional purging/embargo."""
        n = len(df)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        train_indices = list(range(0, max(0, train_end - purge_window)))
        val_indices = list(range(train_end + embargo_window, max(train_end + embargo_window, val_end - purge_window)))
        test_indices = list(range(val_end + embargo_window, n))

        train_df = df.iloc[train_indices].copy()
        val_df = df.iloc[val_indices].copy()
        test_df = df.iloc[test_indices].copy()

        return {
            "status": "PASSED",
            "total_samples": n,
            "train_samples": len(train_df),
            "val_samples": len(val_df),
            "test_samples": len(test_df),
            "purge_window": purge_window,
            "embargo_window": embargo_window,
            "train_df": train_df,
            "val_df": val_df,
            "test_df": test_df,
        }
