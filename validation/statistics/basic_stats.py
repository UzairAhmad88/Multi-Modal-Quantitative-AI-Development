"""
Basic Statistical Primitives & Parametric Confidence Intervals.
"""

import numpy as np
import scipy.stats as stats
from typing import Dict, Any, Tuple


class BasicStatisticsCalculator:
    """
    Calculates summary moments, excess returns, and parametric confidence intervals.
    """

    @staticmethod
    def calculate_moments(returns: np.ndarray) -> Dict[str, float]:
        if len(returns) == 0:
            return {}

        return {
            "mean": round(float(np.mean(returns)), 6),
            "median": round(float(np.median(returns)), 6),
            "std": round(float(np.std(returns, ddof=1)), 6) if len(returns) > 1 else 0.0,
            "skewness": round(float(stats.skew(returns)), 4) if len(returns) > 2 else 0.0,
            "kurtosis": round(float(stats.kurtosis(returns)), 4) if len(returns) > 3 else 0.0,
            "min": round(float(np.min(returns)), 6),
            "max": round(float(np.max(returns)), 6),
            "sample_size": len(returns),
        }

    @staticmethod
    def parametric_confidence_interval(
        returns: np.ndarray, confidence_level: float = 0.95
    ) -> Dict[str, float]:
        if len(returns) < 2:
            return {"mean": 0.0, "lower_bound": 0.0, "upper_bound": 0.0}

        mean = float(np.mean(returns))
        sem = float(stats.sem(returns))
        h = sem * stats.t.ppf((1 + confidence_level) / 2.0, len(returns) - 1)

        return {
            "mean": round(mean, 6),
            "lower_bound": round(mean - h, 6),
            "upper_bound": round(mean + h, 6),
            "confidence_level": confidence_level,
        }

    @staticmethod
    def calculate_excess_returns(
        strategy_returns: np.ndarray, benchmark_returns: np.ndarray
    ) -> np.ndarray:
        min_len = min(len(strategy_returns), len(benchmark_returns))
        return strategy_returns[:min_len] - benchmark_returns[:min_len]
