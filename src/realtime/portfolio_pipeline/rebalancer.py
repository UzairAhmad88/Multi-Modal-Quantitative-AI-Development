"""
Portfolio Rebalancing Engine Module
Translates alpha signals into target asset weights and proposed trade rebalances.
"""

from typing import Dict, List, Any, Optional


class PortfolioRebalancer:
    """Quantitative Portfolio Target Weight Rebalancer."""

    def __init__(self, max_asset_weight: float = 0.25, min_weight_diff: float = 0.02):
        self.max_asset_weight = max_asset_weight
        self.min_weight_diff = min_weight_diff

    def compute_rebalance(
        self,
        signals: List[Dict[str, Any]],
        current_portfolio: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Compute proposed portfolio rebalancing trades.
        """
        total_equity = current_portfolio.get("equity", 100000.0)
        positions = current_portfolio.get("positions", {})

        # Compute raw signal scores
        buy_signals = [s for s in signals if s.get("direction") in ["BUY", "STRONG BUY"]]
        if not buy_signals:
            return []

        target_weight_per_asset = min(self.max_asset_weight, 0.90 / len(buy_signals))

        proposed_trades = []
        for sig in buy_signals:
            symbol = sig["symbol"]
            curr_pos = positions.get(symbol, {})
            curr_weight = curr_pos.get("weight", 0.0)

            target_weight = target_weight_per_asset if sig["direction"] == "BUY" else min(self.max_asset_weight, target_weight_per_asset * 1.2)
            weight_diff = target_weight - curr_weight

            if abs(weight_diff) >= self.min_weight_diff:
                target_value = target_equity = total_equity * target_weight
                curr_value = curr_pos.get("market_value", 0.0)
                order_value = target_value - curr_value

                side = "BUY" if order_value > 0 else "SELL"
                price = sig.get("price", curr_pos.get("price", 150.0))
                quantity = abs(order_value) / price if price > 0 else 0

                proposed_trades.append({
                    "symbol": symbol,
                    "side": side,
                    "target_weight": round(target_weight, 4),
                    "current_weight": round(curr_weight, 4),
                    "weight_diff": round(weight_diff, 4),
                    "proposed_value": round(order_value, 2),
                    "quantity": round(quantity, 2),
                    "price": price,
                    "signal_id": sig.get("signal_id", "SIG-GENERIC")
                })

        return proposed_trades
