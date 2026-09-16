"""
Expected Return Estimator for Transforming Signals and Models into Calibrated Return Forecasts.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional


class ExpectedReturnEstimator:
    """Estimates expected asset returns from raw alpha signals, historical means, or model predictions."""

    @staticmethod
    def estimate_from_signals(
        signals: Dict[str, float],
        target_volatility: float = 0.15,
        method: str = "z_score"
    ) -> Dict[str, float]:
        """Transforms raw alpha signals into annualized expected return estimates."""
        if not signals:
            return {}

        assets = list(signals.keys())
        raw_vals = np.array([signals[a] for a in assets], dtype=float)

        if method == "rank":
            ranks = pd.Series(raw_vals).rank(pct=True).values
            norm_vals = (ranks - 0.5) * 2.0  # [-1, +1]
        elif method == "z_score":
            std = np.std(raw_vals) if np.std(raw_vals) > 1e-6 else 1.0
            mean = np.mean(raw_vals)
            norm_vals = np.clip((raw_vals - mean) / std, -3.0, 3.0) / 3.0
        else:  # raw
            norm_vals = np.clip(raw_vals, -1.0, 1.0)

        # Map normalized signal to expected return scaled by target volatility
        expected_returns = norm_vals * target_volatility
        return {assets[i]: float(expected_returns[i]) for i in range(len(assets))}

    @staticmethod
    def estimate_historical_mean(returns_df: pd.DataFrame, annualize: bool = True) -> Dict[str, float]:
        """Estimates expected return from historical return mean."""
        if returns_df.empty:
            return {}
        means = returns_df.mean()
        if annualize:
            means = means * 252.0
        return means.to_dict()
