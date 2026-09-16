"""
Statistical Tester for Quantitative Returns and Alpha Differences.
Executes parametric and non-parametric hypothesis tests and issues multiple-testing data-snooping warnings.
"""

from typing import Dict, List, Any
import numpy as np
from scipy import stats


class StatisticalTester:
    """Performs statistical hypothesis testing on strategy return series."""

    @staticmethod
    def test_mean_return_significance(returns: List[float], alpha: float = 0.05) -> Dict[str, Any]:
        """T-test for whether mean strategy return is statistically significantly greater than 0."""
        ret_arr = np.array(returns)
        if len(ret_arr) < 5:
            return {"status": "INCONCLUSIVE", "reason": "Sample size too small (< 5 points)"}

        mean_ret = float(np.mean(ret_arr))
        std_ret = float(np.std(ret_arr, ddof=1))
        t_stat, p_val_two = stats.ttest_1samp(ret_arr, 0.0)
        p_val_one = float(p_val_two / 2.0 if t_stat > 0 else 1.0 - p_val_two / 2.0)

        significant = p_val_one < alpha

        return {
            "status": "PASSED" if significant else "NOT_SIGNIFICANT",
            "statistically_significant": significant,
            "mean_return": round(mean_ret, 6),
            "t_statistic": round(float(t_stat), 4),
            "p_value_one_tailed": round(p_val_one, 4),
            "alpha_threshold": alpha,
            "conclusion": "Observed mean return is statistically significantly positive." if significant else "Observed mean return is not statistically distinguishable from zero at alpha=0.05.",
        }

    @staticmethod
    def test_model_difference(returns_a: List[float], returns_b: List[float]) -> Dict[str, Any]:
        """Paired T-test and Wilcoxon signed-rank test comparing Model A vs Model B return series."""
        r_a = np.array(returns_a)
        r_b = np.array(returns_b)
        min_len = min(len(r_a), len(r_b))
        r_a, r_b = r_a[:min_len], r_b[:min_len]

        diff = r_b - r_a
        t_stat, t_pval = stats.ttest_rel(r_b, r_a)

        try:
            w_stat, w_pval = stats.wilcoxon(diff)
        except Exception:
            w_stat, w_pval = 0.0, 1.0

        return {
            "paired_t_test": {"t_statistic": round(float(t_stat), 4), "p_value": round(float(t_pval), 4)},
            "wilcoxon_test": {"w_statistic": round(float(w_stat), 4), "p_value": round(float(w_pval), 4)},
            "models_significantly_different": float(t_pval) < 0.05,
        }

    @staticmethod
    def check_multiple_testing_warning(total_experiments_run: int, max_unadjusted_threshold: int = 20) -> Dict[str, Any]:
        """Issues data-snooping warnings if many hypotheses/experiments were run without p-value adjustment."""
        warning_active = total_experiments_run > max_unadjusted_threshold
        msg = ""
        if warning_active:
            msg = (
                f"MULTIPLE TESTING WARNING: {total_experiments_run} experiments executed. "
                "Running high numbers of unadjusted trials increases false discovery risk (Type I error). "
                "Apply Bonferroni or False Discovery Rate (FDR) adjustments."
            )

        return {
            "warning_active": warning_active,
            "total_experiments_run": total_experiments_run,
            "warning_message": msg,
        }
