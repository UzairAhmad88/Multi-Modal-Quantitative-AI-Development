"""
Transaction Cost Model for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional
import numpy as np


class TransactionCostModel:
    """Computes total estimated transaction costs, commissions, spreads, and market impact penalties."""

    def __init__(
        self,
        commission_bps: float = 5.0,
        bid_ask_spread_bps: float = 5.0,
        market_impact_gamma: float = 0.1,
    ):
        self.commission_bps = commission_bps
        self.bid_ask_spread_bps = bid_ask_spread_bps
        self.market_impact_gamma = market_impact_gamma

    def estimate_cost(
        self,
        target_weights: Dict[str, float],
        current_weights: Dict[str, float],
        portfolio_value: float = 100000.0,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, float]:
        """Calculate linear costs (commission + spread) and non-linear market impact penalty."""
        all_assets = set(target_weights.keys()).union(current_weights.keys())

        linear_cost = 0.0
        impact_cost = 0.0
        total_traded_value = 0.0

        linear_rate = (self.commission_bps + 0.5 * self.bid_ask_spread_bps) / 10000.0

        for asset in all_assets:
            w_new = target_weights.get(asset, 0.0)
            w_old = current_weights.get(asset, 0.0)
            delta_w = abs(w_new - w_old)
            trade_val = delta_w * portfolio_value
            total_traded_value += trade_val

            linear_cost += trade_val * linear_rate

            # Non-linear market impact penalty: gamma * (Trade / ADV)^2 * TradeValue
            meta = (asset_metadata or {}).get(asset, {})
            adv = meta.get("adv", meta.get("liquidity", 1e6))
            if adv > 0:
                participation = trade_val / adv
                impact_cost += self.market_impact_gamma * (participation**2) * trade_val

        total_cost = linear_cost + impact_cost
        cost_bps = (total_cost / portfolio_value * 10000.0) if portfolio_value > 0 else 0.0

        return {
            "total_cost": float(total_cost),
            "linear_cost": float(linear_cost),
            "impact_cost": float(impact_cost),
            "total_traded_value": float(total_traded_value),
            "cost_bps": float(cost_bps),
        }
