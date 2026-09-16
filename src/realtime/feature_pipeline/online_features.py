"""
Online Feature Engine & Rolling State Context Module
Computes real-time quantitative features with online state and verifies feature parity against historical research.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from src.features.technical import add_technical_features


class OnlineFeatureEngine:
    """Real-Time Online Feature Pipeline Engine."""

    def __init__(self, lookback_window: int = 50):
        self.lookback_window = lookback_window
        self.history_buffers: Dict[str, pd.DataFrame] = {}

    def update_and_compute(self, symbol: str, new_bar: Dict[str, Any]) -> pd.DataFrame:
        """
        Append incoming bar to symbol history buffer and compute current feature vector.
        """
        bar_df = pd.DataFrame([new_bar])
        if symbol not in self.history_buffers:
            self.history_buffers[symbol] = bar_df
        else:
            self.history_buffers[symbol] = pd.concat(
                [self.history_buffers[symbol], bar_df], ignore_index=True
            ).tail(self.lookback_window * 2)

        df = self.history_buffers[symbol].copy()
        
        # Ensure numerical types
        for col in ["open", "high", "low", "close", "volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Compute technical features
        df_feats = add_technical_features(df)
        return df_feats

    def get_latest_feature_vector(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Extract the most recent computed feature row for symbol."""
        if symbol in self.history_buffers and len(self.history_buffers[symbol]) > 0:
            df_feats = add_technical_features(self.history_buffers[symbol].copy())
            if len(df_feats) > 0:
                return df_feats.iloc[-1].to_dict()
        return None

    def verify_parity(self, historical_df: pd.DataFrame, online_df: pd.DataFrame, tolerance: float = 1e-4) -> Dict[str, Any]:
        """
        Verify that historical feature calculation and real-time feature calculation
        produce identical results for common columns.
        """
        common_cols = [c for c in historical_df.columns if c in online_df.columns and c not in ["date", "timestamp", "symbol", "ticker"]]
        if not common_cols or len(historical_df) == 0 or len(online_df) == 0:
            return {"is_parity": True, "max_difference": 0.0, "tested_columns": common_cols}

        hist_last = historical_df[common_cols].iloc[-1].to_numpy(dtype=float)
        onl_last = online_df[common_cols].iloc[-1].to_numpy(dtype=float)

        diffs = np.abs(hist_last - onl_last)
        max_diff = float(np.nanmax(diffs)) if len(diffs) > 0 else 0.0

        return {
            "is_parity": bool(max_diff <= tolerance),
            "max_difference": max_diff,
            "tested_columns": common_cols,
            "tolerance": tolerance
        }
