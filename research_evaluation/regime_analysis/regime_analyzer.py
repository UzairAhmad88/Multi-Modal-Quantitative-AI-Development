"""
Regime Analyzer Engine: Evaluates performance breakdown across Bull, Bear, High Volatility, and Low Volatility market regimes.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from research_evaluation.metrics.performance_metrics import PerformanceMetricsEngine


class RegimeAnalyzer:
    """Analyzes strategy returns conditioned on market regime states."""

    def __init__(self):
        self.perf_engine = PerformanceMetricsEngine()

    def analyze_regimes(
        self,
        strategy_returns: List[float],
        market_returns: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Categorizes periods into Bull/Bear/High-Vol/Low-Vol and computes per-regime Sharpe/Return."""
        s_rets = np.array(strategy_returns, dtype=float)
        m_rets = np.array(market_returns, dtype=float) if market_returns else s_rets

        n = min(len(s_rets), len(m_rets))
        if n < 10:
            return {"by_regime": {}}

        s_rets = s_rets[:n]
        m_rets = m_rets[:n]

        m_vol = np.std(m_rets)
        bull_mask = m_rets >= 0
        bear_mask = m_rets < 0
        high_vol_mask = np.abs(m_rets) > m_vol
        low_vol_mask = np.abs(m_rets) <= m_vol

        regimes = {
            "BULL": s_rets[bull_mask],
            "BEAR": s_rets[bear_mask],
            "HIGH_VOLATILITY": s_rets[high_vol_mask],
            "LOW_VOLATILITY": s_rets[low_vol_mask]
        }

        res = {}
        for reg_name, rets_subset in regimes.items():
            if len(rets_subset) > 2:
                eq = np.cumprod(1 + rets_subset) * 100000.0
                perf = self.perf_engine.evaluate_performance(eq)
                res[reg_name] = {
                    "count": len(rets_subset),
                    "mean_daily_return": round(float(np.mean(rets_subset)), 6),
                    "sharpe_ratio": perf["sharpe_ratio"],
                    "win_rate": perf["win_rate"]
                }
            else:
                res[reg_name] = {"count": len(rets_subset), "mean_daily_return": 0.0, "sharpe_ratio": 0.0, "win_rate": 0.0}

        return {"by_regime": res}
