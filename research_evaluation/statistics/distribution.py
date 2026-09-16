"""
Distribution Analysis Engine: Skewness, Kurtosis, VaR, CVaR, and Tail Loss Frequencies.
"""

import numpy as np
from scipy import stats
from typing import List, Dict, Any


class DistributionAnalyzer:
    """Calculates statistical moments and tail loss characteristics."""

    def analyze_distribution(self, returns: List[float], alpha: float = 0.05) -> Dict[str, Any]:
        """Calculates mean, median, skewness, kurtosis, VaR, and CVaR."""
        rets = np.array(returns, dtype=float)
        if len(rets) < 5:
            return {"skewness": 0.0, "kurtosis": 0.0, "var_95": 0.0, "cvar_95": 0.0}

        mean = float(np.mean(rets))
        std = float(np.std(rets))
        skew = float(stats.skew(rets))
        kurt = float(stats.kurtosis(rets))

        var_val = float(np.percentile(rets, alpha * 100))
        cvar_rets = rets[rets <= var_val]
        cvar_val = float(np.mean(cvar_rets)) if len(cvar_rets) > 0 else var_val

        return {
            "mean": round(mean, 6),
            "std": round(std, 6),
            "skewness": round(skew, 4),
            "kurtosis": round(kurt, 4),
            "var_95": round(abs(var_val), 4),
            "cvar_95": round(abs(cvar_val), 4),
            "left_tail_loss_frequency": round(float(np.mean(rets < -0.02)), 4)
        }
