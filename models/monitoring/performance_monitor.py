"""
Model Performance Monitor for Quantitative AI Models.
Tracks rolling Sharpe ratio, accuracy decay, and drawdown accumulation over paper-trading windows.
"""

from typing import Dict, Any, List
import numpy as np


class ModelPerformanceMonitor:
    """Monitors rolling performance decay of paper models."""

    def evaluate_rolling_performance(
        self,
        paper_predictions: np.ndarray,
        realized_returns: np.ndarray,
        window: int = 20
    ) -> Dict[str, Any]:
        """Calculates rolling accuracy and performance metrics."""
        preds = np.array(paper_predictions)
        actuals = np.array(realized_returns)

        if len(preds) < window or len(actuals) < window:
            return {"status": "INSUFFICIENT_DATA", "rolling_metrics": {}}

        recent_preds = preds[-window:]
        recent_acts = actuals[-window:]

        acc = float(np.mean(np.sign(recent_preds) == np.sign(recent_acts)))
        strat_returns = np.sign(recent_preds) * recent_acts
        mean_r = float(np.mean(strat_returns))
        std_r = float(np.std(strat_returns, ddof=1)) if len(strat_returns) > 1 else 0.001
        rolling_sharpe = round((mean_r / (std_r + 1e-6)) * np.sqrt(252), 2)

        is_degraded = acc < 0.45 or rolling_sharpe < 0.0

        return {
            "status": "SUCCESS",
            "window": window,
            "rolling_accuracy": round(acc, 4),
            "rolling_sharpe": rolling_sharpe,
            "performance_degraded": is_degraded
        }
