"""
Hypothesis Tester for Parametric & Non-Parametric Significance Testing and Effect Sizes.
"""

import numpy as np
import scipy.stats as stats
from typing import Dict, Any, List
from validation.schemas.validation_schema import SignificanceResult


class HypothesisTester:
    """
    Executes statistical significance tests and computes effect sizes (Cohen's d).
    """

    @staticmethod
    def one_sample_t_test(
        series: np.ndarray, null_value: float = 0.0, alpha: float = 0.05
    ) -> SignificanceResult:
        if len(series) < 2:
            return SignificanceResult(
                test_name="1-Sample t-Test",
                null_hypothesis=f"Mean return == {null_value}",
                alternative_hypothesis=f"Mean return != {null_value}",
                test_statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                sample_size=len(series),
                is_statistically_significant=False,
            )

        t_stat, p_val = stats.ttest_1samp(series, popmean=null_value)
        std_dev = np.std(series, ddof=1)
        effect_size = (np.mean(series) - null_value) / std_dev if std_dev > 0 else 0.0

        return SignificanceResult(
            test_name="1-Sample t-Test",
            null_hypothesis=f"Mean return == {null_value}",
            alternative_hypothesis=f"Mean return != {null_value}",
            test_statistic=round(float(t_stat), 4),
            p_value=round(float(p_val), 6),
            effect_size=round(float(effect_size), 4),
            effect_size_method="cohens_d",
            sample_size=len(series),
            is_statistically_significant=bool(p_val < alpha),
        )

    @staticmethod
    def paired_sample_t_test(
        series_a: np.ndarray, series_b: np.ndarray, alpha: float = 0.05
    ) -> SignificanceResult:
        min_len = min(len(series_a), len(series_b))
        if min_len < 2:
            return SignificanceResult(
                test_name="Paired t-Test",
                null_hypothesis="Mean diff == 0",
                alternative_hypothesis="Mean diff != 0",
                test_statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                sample_size=min_len,
                is_statistically_significant=False,
            )

        sa = series_a[:min_len]
        sb = series_b[:min_len]
        diff = sa - sb

        t_stat, p_val = stats.ttest_rel(sa, sb)
        std_diff = np.std(diff, ddof=1)
        effect_size = np.mean(diff) / std_diff if std_diff > 0 else 0.0

        return SignificanceResult(
            test_name="Paired t-Test",
            null_hypothesis="Mean diff == 0",
            alternative_hypothesis="Mean diff != 0",
            test_statistic=round(float(t_stat), 4),
            p_value=round(float(p_val), 6),
            effect_size=round(float(effect_size), 4),
            effect_size_method="cohens_d",
            sample_size=min_len,
            is_statistically_significant=bool(p_val < alpha),
        )
