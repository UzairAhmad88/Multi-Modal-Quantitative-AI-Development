"""
Expected Returns Engine Module
Converts raw model predictions, alpha signals, confidence scores, and factor ranks into
normalized, winsorized expected return vectors for quantitative portfolio optimizers.
"""

from typing import Dict, List, Any, Optional, Union
import numpy as np
import pandas as pd
from scipy import stats


class ExpectedReturnModel:
    """Quantitative Expected Return Modeling & Signal Transformation Engine."""

    def __init__(self, method: str = "zscore", winsor_cutoff: float = 0.05):
        self.method = method
        self.winsor_cutoff = winsor_cutoff

    def compute_expected_returns(
        self,
        alpha_signals: Dict[str, float],
        confidence_scores: Optional[Dict[str, float]] = None,
        base_volatilities: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """
        Transform raw alpha predictions into expected annualized returns.
        """
        symbols = list(alpha_signals.keys())
        raw_vals = np.array([alpha_signals[s] for s in symbols], dtype=float)

        if len(raw_vals) == 0:
            return {}

        # 1. Winsorization to eliminate outliers
        if len(raw_vals) >= 4 and self.winsor_cutoff > 0:
            lower = np.percentile(raw_vals, self.winsor_cutoff * 100)
            upper = np.percentile(raw_vals, (1 - self.winsor_cutoff) * 100)
            raw_vals = np.clip(raw_vals, lower, upper)

        # 2. Method Normalization
        if self.method == "zscore":
            std = np.std(raw_vals) + 1e-8
            mean = np.mean(raw_vals)
            norm_vals = (raw_vals - mean) / std
        elif self.method == "rank":
            ranks = stats.rankdata(raw_vals)
            norm_vals = (ranks - np.mean(ranks)) / (np.std(ranks) + 1e-8)
        else:
            norm_vals = raw_vals

        # 3. Confidence Weighting
        if confidence_scores is not None:
            conf_array = np.array([confidence_scores.get(s, 0.50) for s in symbols])
            norm_vals = norm_vals * conf_array

        # 4. Volatility Scaling (assuming ~15% target return scale)
        expected_returns = norm_vals * 0.05

        return {sym: round(float(er), 6) for sym, er in zip(symbols, expected_returns)}
