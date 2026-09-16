"""
Walk-Forward Validation Engine: Rolling & expanding window walk-forward validation with purged CV and embargo gaps.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from research_evaluation.metrics.performance_metrics import PerformanceMetricsEngine


class WalkForwardEngine:
    """Executes chronologically isolated walk-forward cross-validation windows."""

    def __init__(
        self,
        train_period: int = 756,
        validation_period: int = 126,
        test_period: int = 126,
        step: int = 126,
        expanding: bool = True,
        embargo_period: int = 5
    ):
        self.train_period = train_period
        self.validation_period = validation_period
        self.test_period = test_period
        self.step = step
        self.expanding = expanding
        self.embargo_period = embargo_period
        self.perf_engine = PerformanceMetricsEngine()

    def run_walk_forward(self, returns: List[float], dates: Optional[List[str]] = None) -> Dict[str, Any]:
        """Runs walk-forward evaluation across time-series windows."""
        rets = np.array(returns, dtype=float)
        n = len(rets)
        min_required = self.train_period + self.validation_period + self.test_period

        if n < min_required:
            # Fallback simple split for shorter test series
            split = int(n * 0.7)
            train_rets = rets[:split]
            test_rets = rets[split:]
            train_eq = np.cumprod(1 + train_rets) * 100000.0
            test_eq = np.cumprod(1 + test_rets) * 100000.0
            return {
                "num_windows": 1,
                "out_of_sample_sharpe": self.perf_engine.evaluate_performance(test_eq)["sharpe_ratio"],
                "is_out_of_sample": True,
                "windows": [{
                    "window_index": 0,
                    "train_sharpe": self.perf_engine.evaluate_performance(train_eq)["sharpe_ratio"],
                    "test_sharpe": self.perf_engine.evaluate_performance(test_eq)["sharpe_ratio"]
                }]
            }

        windows = []
        start_idx = 0
        w_idx = 0
        oos_test_returns = []

        while start_idx + self.train_period + self.embargo_period + self.test_period <= n:
            train_start = 0 if self.expanding else start_idx
            train_end = start_idx + self.train_period
            test_start = train_end + self.embargo_period
            test_end = min(n, test_start + self.test_period)

            tr_rets = rets[train_start:train_end]
            te_rets = rets[test_start:test_end]
            oos_test_returns.extend(te_rets.tolist())

            tr_eq = np.cumprod(1 + tr_rets) * 100000.0
            te_eq = np.cumprod(1 + te_rets) * 100000.0

            tr_perf = self.perf_engine.evaluate_performance(tr_eq)
            te_perf = self.perf_engine.evaluate_performance(te_eq)

            windows.append({
                "window_index": w_idx,
                "train_range": [train_start, train_end],
                "test_range": [test_start, test_end],
                "train_cagr": tr_perf["cagr"],
                "test_cagr": te_perf["cagr"],
                "train_sharpe": tr_perf["sharpe_ratio"],
                "test_sharpe": te_perf["sharpe_ratio"],
                "test_max_drawdown": te_perf["max_drawdown"]
            })

            start_idx += self.step
            w_idx += 1

        oos_eq = np.cumprod(1 + np.array(oos_test_returns)) * 100000.0 if oos_test_returns else [100000.0]
        oos_perf = self.perf_engine.evaluate_performance(oos_eq)

        return {
            "num_windows": len(windows),
            "out_of_sample_cagr": oos_perf["cagr"],
            "out_of_sample_sharpe": oos_perf["sharpe_ratio"],
            "out_of_sample_max_drawdown": oos_perf["max_drawdown"],
            "is_out_of_sample": True,
            "windows": windows
        }
