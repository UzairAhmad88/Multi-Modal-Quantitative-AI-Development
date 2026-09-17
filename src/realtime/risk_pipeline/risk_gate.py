"""
Pre-Trade Risk Gate Module.
Enforces strict pre-trade risk controls and delegates to HardRiskLimitsEngine to strictly override model decisions.
"""

from typing import Dict, List, Any, Optional, Tuple
from src.realtime.risk_pipeline.hard_limits import HardRiskLimitsEngine, HardRiskConfig


class RealtimeRiskGate:
    """Quantitative Pre-Trade Risk Gate Engine."""

    def __init__(
        self,
        max_position_pct: float = 0.30,
        max_gross_exposure: float = 1.00,
        max_net_exposure: float = 0.50,
        max_drawdown_pct: float = 0.10,
        hard_limits_config: Optional[HardRiskConfig] = None
    ):
        self.max_position_pct = max_position_pct
        self.max_gross_exposure = max_gross_exposure
        self.max_net_exposure = max_net_exposure
        self.max_drawdown_pct = max_drawdown_pct
        self.hard_limits_engine = HardRiskLimitsEngine(config=hard_limits_config)

    def validate_proposed_trade(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any],
        is_data_stale: bool = False
    ) -> Dict[str, Any]:
        """
        Validate proposed order against hard risk limits and active constraints.
        Returns: APPROVED, REJECTED, or REDUCED with detailed reason.
        """
        symbol = trade.get("symbol", "UNKNOWN")
        side = trade.get("side", "BUY")
        quantity = trade.get("quantity", 0.0)
        price = trade.get("price", 150.0)

        # Delegate to HardRiskLimitsEngine first (Hard Limit Override)
        passed, reason, approved_qty = self.hard_limits_engine.check_order_limits(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            portfolio=portfolio,
            is_data_stale=is_data_stale
        )

        if not passed:
            return {
                "decision": "REJECTED",
                "symbol": symbol,
                "reason": reason,
                "approved_quantity": 0.0
            }

        if approved_qty < quantity and approved_qty > 0:
            return {
                "decision": "REDUCED",
                "symbol": symbol,
                "reason": reason,
                "approved_quantity": round(approved_qty, 2)
            }

        return {
            "decision": "APPROVED",
            "symbol": symbol,
            "reason": reason,
            "approved_quantity": round(approved_qty, 2)
        }
