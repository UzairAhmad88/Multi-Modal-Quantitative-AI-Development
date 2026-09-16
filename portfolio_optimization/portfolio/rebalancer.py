"""
Rebalancing Engine for Generating Executable Rebalance Orders and Trade Vectors.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class RebalancingEngine:
    """Generates rebalancing trade vectors using threshold rules and no-trade zones."""

    def __init__(self, rebalance_threshold: float = 0.02):
        self.rebalance_threshold = rebalance_threshold

    def generate_rebalance_orders(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        asset_prices: Dict[str, float],
        portfolio_value: float = 100000.0
    ) -> Dict[str, Any]:
        """Generates order share quantities and target allocations."""
        all_assets = set(current_weights.keys()).union(set(target_weights.keys()))
        orders = []
        total_trade_val = 0.0

        for a in all_assets:
            w_curr = current_weights.get(a, 0.0)
            w_targ = target_weights.get(a, 0.0)
            diff = w_targ - w_curr

            if abs(diff) < self.rebalance_threshold:
                continue  # In no-trade zone

            price = asset_prices.get(a, 100.0)
            target_cash_alloc = diff * portfolio_value
            shares = int(np.floor(target_cash_alloc / price)) if price > 0 else 0

            orders.append({
                "symbol": a,
                "current_weight": round(w_curr, 4),
                "target_weight": round(w_targ, 4),
                "weight_change": round(diff, 4),
                "side": "BUY" if diff > 0 else "SELL",
                "shares": shares,
                "price": price,
                "trade_value": round(abs(shares * price), 2)
            })
            total_trade_val += abs(shares * price)

        return {
            "rebalance_required": len(orders) > 0,
            "orders_count": len(orders),
            "total_trade_value": round(total_trade_val, 2),
            "orders": orders
        }
