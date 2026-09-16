"""
Robustness Engine: Evaluates overall strategy stability across periods, assets, costs, regimes, and parameters.
"""

import numpy as np
from typing import List, Dict, Any
from research_evaluation.metrics.performance_metrics import PerformanceMetricsEngine
from research_evaluation.sensitivity.sensitivity_engine import SensitivityEngine
from research_evaluation.regime_analysis.regime_analyzer import RegimeAnalyzer


class RobustnessEngine:
    """Comprehensive strategy robustness evaluator."""

    def __init__(self):
        self.perf_engine = PerformanceMetricsEngine()
        self.sens_engine = SensitivityEngine()
        self.reg_analyzer = RegimeAnalyzer()

    def evaluate_robustness(
        self,
        returns: List[float],
        market_returns: List[float] = None
    ) -> Dict[str, Any]:
        """Evaluates robustness index, cost stability, and regime consistency."""
        rets = np.array(returns, dtype=float)
        eq = np.cumprod(1 + rets) * 100000.0 if len(rets) > 0 else [100000.0]
        base_perf = self.perf_engine.evaluate_performance(eq)

        cost_res = self.sens_engine.run_cost_sensitivity(returns, cost_grid_bps=[0.0, 5.0, 10.0, 20.0])
        reg_res = self.reg_analyzer.analyze_regimes(returns, market_returns=market_returns)

        # Robustness score computation (0 to 100)
        sharpe = base_perf["sharpe_ratio"]
        sharpe_score = min(40.0, max(0.0, sharpe * 20.0))
        win_score = min(30.0, base_perf["win_rate"] * 30.0)
        dd_score = min(30.0, max(0.0, (1.0 - base_perf["max_drawdown"]) * 30.0))

        robustness_score = round(sharpe_score + win_score + dd_score, 1)

        return {
            "robustness_score": robustness_score,
            "is_robust": bool(robustness_score >= 60.0 and base_perf["sharpe_ratio"] >= 1.0),
            "base_performance": base_perf,
            "cost_sensitivity": cost_res,
            "regime_performance": reg_res
        }
