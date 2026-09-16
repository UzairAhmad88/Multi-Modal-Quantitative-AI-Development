"""
Liquidity & ADV Participation Constraint for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional, Tuple
from portfolio.constraints.base import BaseConstraint


class LiquidityConstraint(BaseConstraint):
    """Enforces participation rate limits relative to Average Daily Volume (ADV)."""

    def __init__(self, max_adv_participation: float = 0.10, portfolio_value: float = 100000.0):
        super().__init__("LiquidityConstraint")
        self.max_adv_participation = max_adv_participation
        self.portfolio_value = portfolio_value

    def validate(
        self,
        weights: Dict[str, float],
        current_weights: Optional[Dict[str, float]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Tuple[bool, str]:
        if not asset_metadata:
            return True, "No liquidity metadata available"

        curr = current_weights or {}
        for asset, w in weights.items():
            trade_w = abs(w - curr.get(asset, 0.0))
            trade_value = trade_w * self.portfolio_value
            meta = asset_metadata.get(asset, {})
            adv = meta.get("adv", meta.get("liquidity", 0.0))

            if adv > 0:
                max_trade_val = adv * self.max_adv_participation
                if trade_value > max_trade_val + 1e-5:
                    return (
                        False,
                        f"Asset '{asset}' trade value ${trade_value:,.2f} exceeds {self.max_adv_participation*100}% ADV limit (${max_trade_val:,.2f})",
                    )

        return True, "Liquidity constraints satisfied"
