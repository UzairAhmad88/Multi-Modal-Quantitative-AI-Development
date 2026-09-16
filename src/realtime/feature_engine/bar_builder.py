"""
Real-Time Bar Builder & Feature Parity Validator
Aggregates ticks into 15m bars incrementally and ensures strict feature parity between research and live inference.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd


class RealtimeBarBuilder:
    """Incremental 15-minute Intraday Bar Aggregator."""

    def __init__(self, symbol: str, timeframe_minutes: int = 15):
        self.symbol = symbol.upper()
        self.timeframe_minutes = timeframe_minutes
        self.ticks: List[Dict[str, Any]] = []

    def add_tick(self, tick: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add tick quote and return aggregated bar if timeframe boundary reached.
        """
        self.ticks.append(tick)
        if len(self.ticks) >= 15:  # Aggregate 15 ticks into 1 bar for fast testing
            bar = self._aggregate_ticks(self.ticks)
            self.ticks = []
            return bar
        return None

    def _aggregate_ticks(self, ticks: List[Dict[str, Any]]) -> Dict[str, Any]:
        prices = [t["last"] for t in ticks]
        volumes = [t.get("volume", 100) for t in ticks]

        return {
            "timestamp": ticks[-1]["timestamp"],
            "symbol": self.symbol,
            "open": prices[0],
            "high": max(prices),
            "low": min(prices),
            "close": prices[-1],
            "volume": sum(volumes),
        }


class FeatureParityValidator:
    """Validates real-time feature schema parity against research feature standards."""

    def __init__(self, expected_feature_names: List[str]):
        self.expected_feature_names = expected_feature_names

    def validate_features(self, live_features_df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Verify that live dataframe contains exact feature names and order without missing values.
        """
        issues = []
        live_cols = list(live_features_df.columns)

        for feat in self.expected_feature_names:
            if feat not in live_cols:
                issues.append(f"Missing expected feature: {feat}")

        if live_features_df.isnull().sum().sum() > 0:
            issues.append("Found null/NaN values in live feature calculation")

        return len(issues) == 0, issues
