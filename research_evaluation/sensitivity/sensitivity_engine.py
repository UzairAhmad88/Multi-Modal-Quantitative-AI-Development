"""
Sensitivity Engine: Grid testing over transaction costs, slippage, risk aversion, position limits, and rebalance frequencies.
"""

import numpy as np
from typing import List, Dict, Any
from research_evaluation.metrics.performance_metrics import PerformanceMetricsEngine


class SensitivityEngine:
    """Evaluates strategy sensitivity to transaction costs and parameter changes."""

    def __init__(self):
        self.perf_engine = PerformanceMetricsEngine()

    def run_cost_sensitivity(
        self,
        gross_returns: List[float],
        cost_grid_bps: List[float] = [0.0, 2.0, 5.0, 10.0, 20.0],
        turnover_daily: float = 0.05
    ) -> Dict[str, Any]:
        """Evaluates net performance across varying transaction cost thresholds."""
        rets = np.array(gross_returns, dtype=float)
        results = []

        for cost_bps in cost_grid_bps:
            daily_cost = (cost_bps / 10000.0) * turnover_daily
            net_rets = rets - daily_cost
            eq = np.cumprod(1 + net_rets) * 100000.0
            perf = self.perf_engine.evaluate_performance(eq)

            results.append({
                "cost_bps": cost_bps,
                "daily_cost_bps": round(daily_cost * 10000.0, 4),
                "net_cagr": perf["cagr"],
                "net_sharpe": perf["sharpe_ratio"],
                "max_drawdown": perf["max_drawdown"]
            })

        return {
            "turnover_daily": turnover_daily,
            "cost_sensitivity_grid": results
        }
