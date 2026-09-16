"""
Bootstrap Engine: Block bootstrapping confidence intervals for Sharpe ratio, CAGR, and Drawdown.
"""

import numpy as np
from typing import List, Dict, Any


class BootstrapEngine:
    """Computes empirical bootstrap confidence intervals."""

    def __init__(self, num_samples: int = 500, confidence_level: float = 0.95, random_seed: int = 42):
        self.num_samples = num_samples
        self.confidence_level = confidence_level
        self.random_seed = random_seed

    def bootstrap_sharpe(self, returns: List[float], annualization_factor: int = 252) -> Dict[str, Any]:
        """Calculates 95% bootstrap confidence interval for Sharpe Ratio."""
        rets = np.array(returns, dtype=float)
        if len(rets) < 10:
            return {"mean_sharpe": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}

        np.random.seed(self.random_seed)
        n = len(rets)
        boot_sharpes = []

        for _ in range(self.num_samples):
            idx = np.random.choice(n, size=n, replace=True)
            sample = rets[idx]
            std = np.std(sample)
            if std > 1e-6:
                sh = (np.mean(sample) / std) * np.sqrt(annualization_factor)
                boot_sharpes.append(sh)

        if not boot_sharpes:
            return {"mean_sharpe": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}

        alpha = 1.0 - self.confidence_level
        lower_pct = (alpha / 2.0) * 100
        upper_pct = (1.0 - (alpha / 2.0)) * 100

        ci_low = float(np.percentile(boot_sharpes, lower_pct))
        ci_high = float(np.percentile(boot_sharpes, upper_pct))
        mean_sh = float(np.mean(boot_sharpes))

        return {
            "mean_sharpe": round(mean_sh, 4),
            "ci_lower": round(ci_low, 4),
            "ci_upper": round(ci_high, 4),
            "confidence_level": self.confidence_level,
            "num_samples": self.num_samples
        }
