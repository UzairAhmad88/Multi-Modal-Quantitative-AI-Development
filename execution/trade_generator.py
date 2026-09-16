"""
Trade Generator Module: Transforms Target Portfolio Weights into Required Trade Signals & Quantities.
"""

from typing import Dict, Any, List
from execution.orders.order_types import OrderSide


class TradeGenerator:
    """Converts portfolio weight differentials into discrete trade orders."""

    def __init__(self, allow_fractional: bool = True, round_shares: bool = False):
        self.allow_fractional = allow_fractional
        self.round_shares = round_shares

    def generate_trades(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        prices: Dict[str, float],
        portfolio_value: float = 100000.0
    ) -> List[Dict[str, Any]]:
        """Generates required trade signals and quantities for rebalancing."""
        all_assets = sorted(list(set(current_weights.keys()).union(set(target_weights.keys()))))
        trades = []

        for asset in all_assets:
            price = prices.get(asset, 100.0)
            if price <= 0:
                continue

            w_curr = current_weights.get(asset, 0.0)
            w_targ = target_weights.get(asset, 0.0)
            delta_w = w_targ - w_curr

            curr_val = w_curr * portfolio_value
            targ_val = w_targ * portfolio_value
            trade_val = targ_val - curr_val

            raw_qty = trade_val / price
            qty = abs(raw_qty)

            if self.round_shares or not self.allow_fractional:
                qty = float(round(qty))

            if qty <= 1e-6:
                side = OrderSide.HOLD
            elif delta_w > 0:
                if w_curr < 0:
                    side = OrderSide.COVER if w_targ >= 0 else OrderSide.BUY
                else:
                    side = OrderSide.BUY
            else:
                if w_curr > 0 and w_targ <= 0:
                    side = OrderSide.SELL
                elif w_targ < 0:
                    side = OrderSide.SHORT
                else:
                    side = OrderSide.SELL

            if side != OrderSide.HOLD and qty > 0:
                trades.append({
                    "asset": asset,
                    "side": side,
                    "quantity": qty,
                    "price": price,
                    "trade_value": abs(trade_val),
                    "current_weight": w_curr,
                    "target_weight": w_targ,
                    "delta_weight": delta_w
                })

        return trades
