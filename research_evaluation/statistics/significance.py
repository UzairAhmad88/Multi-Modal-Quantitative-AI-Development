"""
Statistical Significance Engine: t-tests, p-values, and multiple testing adjustments.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, List


class SignificanceTester:
    """Performs hypothesis testing on strategy return distribution."""

    def test_significance(self, returns: List[float], mu_null: float = 0.0) -> Dict[str, Any]:
        """Runs 1-sample t-test testing whether mean return is significantly > mu_null."""
        rets = np.array(returns, dtype=float)
        if len(rets) < 5:
            return {"t_statistic": 0.0, "p_value": 1.0, "is_statistically_significant": False}

        t_stat, p_two_tail = stats.ttest_1samp(rets, mu_null)
        p_one_tail = p_two_tail / 2.0 if t_stat > 0 else 1.0 - (p_two_tail / 2.0)

        return {
            "t_statistic": round(float(t_stat), 4),
            "p_value_one_tailed": round(float(p_one_tail), 6),
            "p_value_two_tailed": round(float(p_two_tail), 6),
            "is_statistically_significant": bool(p_one_tail < 0.05),
            "sample_size": len(rets)
        }
