"""
Benchmark Engine: Evaluates strategy performance relative to Buy & Hold, Equal Weight, and Market Baselines.
"""

import numpy as np
from typing import List, Dict, Any, Union
from research_evaluation.metrics.performance_metrics import PerformanceMetricsEngine


class BenchmarkEngine:
    """Calculates relative performance metrics: Alpha, Beta, Tracking Error, Information Ratio."""

    def __init__(self, annualization_factor: int = 252):
        self.annualization_factor = annualization_factor
        self.perf_engine = PerformanceMetricsEngine(annualization_factor=annualization_factor)

    def evaluate_against_benchmark(
        self,
        strategy_returns: List[float],
        benchmark_returns: List[float]
    ) -> Dict[str, Any]:
        """Calculates Alpha, Beta, R-squared, Tracking Error, and Information Ratio."""
        s_rets = np.array(strategy_returns, dtype=float)
        b_rets = np.array(benchmark_returns, dtype=float)

        min_len = min(len(s_rets), len(b_rets))
        if min_len < 5:
            return {"alpha": 0.0, "beta": 1.0, "information_ratio": 0.0, "tracking_error": 0.0}

        s_rets = s_rets[:min_len]
        b_rets = b_rets[:min_len]

        cov = np.cov(s_rets, b_rets)
        var_b = cov[1, 1]
        beta = float(cov[0, 1] / var_b) if var_b > 1e-8 else 1.0

        r_sq = float((cov[0, 1] ** 2) / (cov[0, 0] * cov[1, 1])) if cov[0, 0] * cov[1, 1] > 1e-8 else 0.0

        diff_rets = s_rets - b_rets
        active_return = float(np.mean(diff_rets) * self.annualization_factor)
        tracking_error = float(np.std(diff_rets) * np.sqrt(self.annualization_factor))
        info_ratio = float(active_return / tracking_error) if tracking_error > 1e-6 else 0.0

        alpha = float((np.mean(s_rets) - beta * np.mean(b_rets)) * self.annualization_factor)

        return {
            "alpha": round(alpha, 4),
            "beta": round(beta, 4),
            "r_squared": round(r_sq, 4),
            "active_return": round(active_return, 4),
            "tracking_error": round(tracking_error, 4),
            "information_ratio": round(info_ratio, 4)
        }
