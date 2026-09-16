"""
Transaction Cost & Market Impact Model Module
Calculates commission fees, spread drag, and square-root market impact costs for portfolio trades.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd


class CostModel:
    """Quantitative Transaction Cost & Market Impact Engine."""

    def __init__(
        self,
        commission_bps: float = 10.0,
        slippage_bps: float = 5.0,
        impact_coefficient: float = 0.10,
    ):
        self.commission_bps = commission_bps
        self.slippage_bps = slippage_bps
        self.impact_coefficient = impact_coefficient

    def compute_trade_cost(
        self,
        trade_value: float,
        daily_volume_value: float = 10000000.0,
    ) -> Dict[str, float]:
        """
        Calculate total execution cost including commission, spread, and square-root market impact.
        """
        if trade_value <= 0:
            return {"commission": 0.0, "slippage": 0.0, "market_impact": 0.0, "total_cost": 0.0}

        comm = trade_value * (self.commission_bps / 10000.0)
        slip = trade_value * (self.slippage_bps / 10000.0)

        # Square-root Market Impact Model: Impact ~ gamma * sqrt(Trade Value / Daily Volume Value)
        participation_rate = max(1e-6, trade_value / (daily_volume_value + 1e-8))
        impact_bps = self.impact_coefficient * np.sqrt(participation_rate) * 10000.0
        impact = trade_value * (impact_bps / 10000.0)

        total = comm + slip + impact

        return {
            "commission": round(float(comm), 2),
            "slippage": round(float(slip), 2),
            "market_impact": round(float(impact), 2),
            "total_cost": round(float(total), 2),
        }
