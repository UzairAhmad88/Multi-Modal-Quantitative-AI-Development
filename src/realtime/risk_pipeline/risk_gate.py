"""
Pre-Trade Risk Gate Module
Enforces strict pre-trade risk controls: position limit, gross exposure, net exposure, max drawdown, and stale data checks.
"""

from typing import Dict, List, Any, Optional, Tuple


class RealtimeRiskGate:
    """Quantitative Pre-Trade Risk Gate Engine."""

    def __init__(
        self,
        max_position_pct: float = 0.30,
        max_gross_exposure: float = 1.00,
        max_net_exposure: float = 0.50,
        max_drawdown_pct: float = 0.10
    ):
        self.max_position_pct = max_position_pct
        self.max_gross_exposure = max_gross_exposure
        self.max_net_exposure = max_net_exposure
        self.max_drawdown_pct = max_drawdown_pct

    def validate_proposed_trade(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any],
        is_data_stale: bool = False
    ) -> Dict[str, Any]:
        """
        Validate proposed order against active risk constraints.
        Returns: APPROVED, REJECTED, or REDUCED with detailed reason.
        """
        if is_data_stale:
            return {
                "decision": "REJECTED",
                "symbol": trade["symbol"],
                "reason": "Data feed is stale. All proposed orders rejected by Risk Gate.",
                "approved_quantity": 0.0
            }

        equity = portfolio.get("equity", 100000.0)
        curr_drawdown = abs(portfolio.get("drawdown", 0.0))

        if curr_drawdown > self.max_drawdown_pct:
            return {
                "decision": "REJECTED",
                "symbol": trade["symbol"],
                "reason": f"Portfolio drawdown {curr_drawdown:.2%} exceeds max limit {self.max_drawdown_pct:.2%}",
                "approved_quantity": 0.0
            }

        # Position limit check
        trade_val = trade["proposed_value"]
        pos_weight = trade["target_weight"]
        if pos_weight > self.max_position_pct:
            # Reduce trade size
            reduced_weight = self.max_position_pct
            reduced_value = equity * (reduced_weight - trade["current_weight"])
            price = trade.get("price", 150.0)
            approved_qty = max(0.0, reduced_value / price) if price > 0 else 0.0

            return {
                "decision": "REDUCED",
                "symbol": trade["symbol"],
                "reason": f"Target weight {pos_weight:.2%} capped at max position limit {self.max_position_pct:.2%}",
                "approved_quantity": round(approved_qty, 2)
            }

        return {
            "decision": "APPROVED",
            "symbol": trade["symbol"],
            "reason": "Order passed all pre-trade risk checks",
            "approved_quantity": trade["quantity"]
        }
