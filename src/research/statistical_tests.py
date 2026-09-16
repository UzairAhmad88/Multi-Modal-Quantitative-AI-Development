"""
Statistical Hypothesis Testing & Bootstrapping Module
Performs parametric t-tests, non-parametric Wilcoxon tests, and bootstrap confidence interval estimation.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


class StatisticalTester:
    """Quantitative Hypothesis Testing & Resampling Engine."""

    def __init__(self, strategy_returns: pd.Series, benchmark_returns: Optional[pd.Series] = None):
        """
        Initialize StatisticalTester.
        :param strategy_returns: Daily strategy return series.
        :param benchmark_returns: Daily benchmark return series (e.g., S&P 500 / Buy & Hold).
        """
        self.strat_rets = strategy_returns.dropna().copy()
        if benchmark_returns is not None:
            self.bench_rets = benchmark_returns.dropna().copy()
        else:
            self.bench_rets = pd.Series(0.0, index=self.strat_rets.index)

    def test_performance_significance(self) -> Dict[str, Any]:
        """
        Run paired t-test and Wilcoxon signed-rank test against zero and against benchmark returns.
        """
        strat = self.strat_rets.values
        bench = self.bench_rets.reindex(self.strat_rets.index).fillna(0.0).values

        if len(strat) < 5:
            return {
                "t_stat_vs_zero": 0.0,
                "p_val_vs_zero": 1.0,
                "wilcoxon_stat_vs_zero": 0.0,
                "wilcoxon_p_val_vs_zero": 1.0,
            }

        # Test vs Zero
        t_stat_0, p_val_0 = stats.ttest_1samp(strat, 0.0)
        try:
            w_stat_0, w_p_val_0 = stats.wilcoxon(strat[strat != 0])
        except Exception:
            w_stat_0, w_p_val_0 = 0.0, 1.0

        # Test vs Benchmark
        diff = strat - bench
        if len(diff[diff != 0]) > 5:
            t_stat_b, p_val_b = stats.ttest_1samp(diff, 0.0)
            try:
                w_stat_b, w_p_val_b = stats.wilcoxon(diff[diff != 0])
            except Exception:
                w_stat_b, w_p_val_b = 0.0, 1.0
        else:
            t_stat_b, p_val_b, w_stat_b, w_p_val_b = 0.0, 1.0, 0.0, 1.0

        return {
            "t_stat_vs_zero": round(float(t_stat_0), 4),
            "p_val_vs_zero": round(float(p_val_0), 4),
            "is_significant_vs_zero_95": bool(p_val_0 < 0.05),
            "wilcoxon_p_val_vs_zero": round(float(w_p_val_0), 4),
            "t_stat_vs_benchmark": round(float(t_stat_b), 4),
            "p_val_vs_benchmark": round(float(p_val_b), 4),
            "is_significant_vs_benchmark_95": bool(p_val_b < 0.05),
        }

    def bootstrap_metrics(
        self, num_iterations: int = 1000, ci_level: float = 0.95
    ) -> Dict[str, Dict[str, float]]:
        """
        Non-parametric bootstrap resampling to calculate confidence intervals for Sharpe, CAGR, and Drawdown.
        """
        rets = self.strat_rets.values
        if len(rets) < 10:
            return {
                "sharpe": {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0},
                "cagr": {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0},
                "max_drawdown": {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0},
            }

        np.random.seed(42)
        n = len(rets)
        sharpe_boot = []
        cagr_boot = []
        dd_boot = []

        alpha = (1.0 - ci_level) / 2.0

        for _ in range(num_iterations):
            sample = np.random.choice(rets, size=n, replace=True)
            ann_mean = sample.mean() * 252
            ann_std = sample.std() * np.sqrt(252) + 1e-8
            sharpe = ann_mean / ann_std
            cagr = np.expm1(np.sum(np.log1p(np.maximum(-0.99, sample))))

            cum = np.cumprod(1 + sample)
            peak = np.maximum.accumulate(cum)
            dd = np.min((cum - peak) / peak)

            sharpe_boot.append(sharpe)
            cagr_boot.append(cagr)
            dd_boot.append(dd)

        def get_ci(arr):
            lower = float(np.percentile(arr, alpha * 100))
            upper = float(np.percentile(arr, (1.0 - alpha) * 100))
            mean_val = float(np.mean(arr))
            return {"mean": round(mean_val, 4), "ci_lower": round(lower, 4), "ci_upper": round(upper, 4)}

        return {
            "sharpe": get_ci(sharpe_boot),
            "cagr": get_ci(cagr_boot),
            "max_drawdown": get_ci(dd_boot),
        }
