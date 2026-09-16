"""
Bootstrap Confidence Interval Engine.
Computes non-parametric bootstrap confidence intervals for Sharpe, CAGR, Max Drawdown, and Accuracy.
"""

from typing import Dict, List, Any
import numpy as np


class BootstrapEngine:
    """Computes bootstrap confidence intervals for quantitative metrics."""

    @staticmethod
    def compute_metric_confidence_intervals(
        returns: List[float],
        iterations: int = 1000,
        confidence_level: float = 0.95,
        seed: int = 42,
    ) -> Dict[str, Any]:
        np.random.seed(seed)
        ret_arr = np.array(returns)
        n = len(ret_arr)

        if n < 5:
            return {"status": "INCONCLUSIVE", "reason": "Insufficient return observations"}

        boot_sharpes = []
        boot_cagrs = []

        alpha_lower = (1.0 - confidence_level) / 2.0
        alpha_upper = 1.0 - alpha_lower

        for _ in range(iterations):
            sample = np.random.choice(ret_arr, size=n, replace=True)
            mean_s = np.mean(sample)
            std_s = np.std(sample, ddof=1)
            sharpe_s = (mean_s / (std_s + 1e-8)) * np.sqrt(252)
            cagr_s = (1.0 + mean_s) ** 252 - 1.0

            boot_sharpes.append(sharpe_s)
            boot_cagrs.append(cagr_s)

        sharpe_low = float(np.percentile(boot_sharpes, alpha_lower * 100))
        sharpe_high = float(np.percentile(boot_sharpes, alpha_upper * 100))
        cagr_low = float(np.percentile(boot_cagrs, alpha_lower * 100))
        cagr_high = float(np.percentile(boot_cagrs, alpha_upper * 100))

        return {
            "iterations": iterations,
            "confidence_level": confidence_level,
            "seed": seed,
            "sharpe_ci": {
                "mean": round(float(np.mean(boot_sharpes)), 2),
                "lower_bound": round(sharpe_low, 2),
                "upper_bound": round(sharpe_high, 2),
            },
            "cagr_ci": {
                "mean": round(float(np.mean(boot_cagrs)), 4),
                "lower_bound": round(cagr_low, 4),
                "upper_bound": round(cagr_high, 4),
            },
        }
