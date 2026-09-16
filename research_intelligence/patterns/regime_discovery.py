"""
Regime Discovery Engine for Regime-Conditional Pattern Evaluation.
Segments pattern performance across market regimes (bullish trend, bearish trend, high volatility, low volatility).
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


class RegimeDiscoveryEngine:
    """Evaluates relationship stability conditionally across detected market regimes."""

    def analyze_regime_conditions(
        self,
        df: pd.DataFrame,
        regime_col: str = "regime",
        feature_col: str = "news_sentiment",
        target_col: str = "returns"
    ) -> Dict[str, Any]:
        """Calculates conditional statistics per regime cluster."""
        if df.empty or feature_col not in df.columns or target_col not in df.columns:
            return {"status": "INVALID_INPUT", "regime_breakdown": {}}

        # If regime column missing, synthesize basic volatility-trend regime
        if regime_col not in df.columns:
            df = df.copy()
            returns = df[target_col]
            vol = returns.rolling(10, min_periods=3).std().fillna(returns.std())
            median_vol = vol.median()
            df["regime"] = np.where(vol > median_vol, "HIGH_VOLATILITY", "LOW_VOLATILITY")
            regime_col = "regime"

        grouped = df.groupby(regime_col)
        breakdown = {}

        for regime_name, group in grouped:
            if len(group) < 5:
                continue
            corr = float(group[feature_col].corr(group[target_col]))
            mean_ret = float(group[target_col].mean())
            vol_ret = float(group[target_col].std())

            breakdown[str(regime_name)] = {
                "count": len(group),
                "correlation": round(corr, 4) if not np.isnan(corr) else 0.0,
                "mean_target_return": round(mean_ret, 4),
                "target_volatility": round(vol_ret, 4)
            }

        return {
            "status": "SUCCESS",
            "feature": feature_col,
            "target": target_col,
            "regime_breakdown": breakdown
        }
