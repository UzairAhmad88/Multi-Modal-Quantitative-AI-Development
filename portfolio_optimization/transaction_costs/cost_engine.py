"""
Transaction Cost Engine for Calculating Commission, Spread, Slippage, and Market Impact Costs.
"""

import numpy as np
from typing import Dict, Any, Optional


class TransactionCostEngine:
    """Calculates granular transaction cost breakdown for portfolio rebalancing trades."""

    def __init__(
        self,
        commission_bps: float = 1.0,
        slippage_bps: float = 5.0,
        spread_bps: float = 2.0
    ):
        self.commission_bps = commission_bps
        self.slippage_bps = slippage_bps
        self.spread_bps = spread_bps

    def calculate_trade_cost(
        self,
        target_weights: Dict[str, float],
        current_weights: Dict[str, float],
        portfolio_value: float = 100000.0
    ) -> Dict[str, Any]:
        """Calculates turnover, trade volume, commission, slippage, and total cost breakdown."""
        all_assets = set(target_weights.keys()).union(set(current_weights.keys()))
        trades = {}
        total_trade_volume = 0.0

        for a in all_assets:
            w_t = target_weights.get(a, 0.0)
            w_c = current_weights.get(a, 0.0)
            delta_w = w_t - w_c
            trade_val = abs(delta_w) * portfolio_value
            trades[a] = {
                "weight_change": round(delta_w, 6),
                "trade_value": round(trade_val, 2),
                "direction": "BUY" if delta_w > 0 else ("SELL" if delta_w < 0 else "HOLD")
            }
            total_trade_volume += trade_val

        turnover = total_trade_volume / portfolio_value if portfolio_value > 0 else 0.0
        commission = total_trade_volume * (self.commission_bps / 10000.0)
        slippage = total_trade_volume * (self.slippage_bps / 10000.0)
        spread = total_trade_volume * (self.spread_bps / 10000.0)
        total_cost = commission + slippage + spread

        return {
            "portfolio_value": portfolio_value,
            "total_trade_volume": round(total_trade_volume, 2),
            "turnover": round(turnover, 4),
            "commission_cost": round(commission, 2),
            "slippage_cost": round(slippage, 2),
            "spread_cost": round(spread, 2),
            "total_cost": round(total_cost, 2),
            "total_cost_bps": round((total_cost / portfolio_value) * 10000.0, 2) if portfolio_value > 0 else 0.0,
            "asset_trades": trades
        }
