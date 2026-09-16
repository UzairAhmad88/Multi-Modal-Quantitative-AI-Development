"""
Historical Stress Testing Engine for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from risk.core.risk_result import StressTestResult


class HistoricalStressEngine:
    """Replays historical market return windows against target portfolio weights."""

    @staticmethod
    def run_historical_stress(
        scenario_id: str,
        portfolio_id: str,
        weights: Dict[str, float],
        historical_returns: np.ndarray,
        base_value: float = 100000.0,
    ) -> StressTestResult:
        """Apply historical return sequence R_hist to base value: V_stressed = V_base * prod(1 + R_port)."""
        rets = np.array(historical_returns, dtype=float)
        assets = list(weights.keys())
        w_vec = np.array([weights[a] for a in assets], dtype=float)

        if rets.ndim == 2 and rets.shape[1] == len(assets):
            port_rets = rets @ w_vec
        elif rets.ndim == 1:
            port_rets = rets
        else:
            port_rets = np.zeros(10)

        cum_factor = float(np.prod(1.0 + port_rets))
        stressed_val = base_value * cum_factor
        abs_loss = float(max(0.0, base_value - stressed_val))
        pct_loss = float(abs_loss / base_value) if base_value > 0 else 0.0

        return StressTestResult(
            scenario_id=scenario_id,
            portfolio_id=portfolio_id,
            base_value=base_value,
            stressed_value=stressed_val,
            absolute_loss=abs_loss,
            percentage_loss=pct_loss,
            risk_metrics={"max_drawdown": float(np.max((np.maximum.accumulate(cum_factor) - cum_factor))), "cum_factor": cum_factor},
        )
