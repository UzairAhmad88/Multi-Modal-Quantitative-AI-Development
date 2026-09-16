"""
Strategy & Model Comparison Engine: Compiles side-by-side performance matrix for multiple models/strategies.
"""

import numpy as np
from typing import Dict, Any, List
from research_evaluation.metrics.performance_metrics import PerformanceMetricsEngine


class StrategyComparisonEngine:
    """Builds side-by-side strategy and model metrics comparison matrix."""

    def __init__(self):
        self.perf_engine = PerformanceMetricsEngine()

    def compare_strategies(
        self,
        strategies_returns: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Compares multiple strategies across raw metrics without arbitrary single rankings."""
        comparison_matrix = {}

        for strat_name, rets in strategies_returns.items():
            eq = np.cumprod(1 + np.array(rets, dtype=float)) * 100000.0
            perf = self.perf_engine.evaluate_performance(eq)
            comparison_matrix[strat_name] = {
                "cagr": perf["cagr"],
                "volatility": perf["annualized_volatility"],
                "sharpe_ratio": perf["sharpe_ratio"],
                "sortino_ratio": perf["sortino_ratio"],
                "max_drawdown": perf["max_drawdown"],
                "calmar_ratio": perf["calmar_ratio"],
                "win_rate": perf["win_rate"],
                "profit_factor": perf["profit_factor"]
            }

        return {"strategy_comparison": comparison_matrix}
