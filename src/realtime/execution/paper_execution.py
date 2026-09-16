"""
Paper Execution Engine Module
Simulates order submission, fills, partial fills, slippage, and transaction commissions.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Any, Optional


class PaperExecutionEngine:
    """Quantitative Paper Order Execution Engine."""

    def __init__(self, slippage_bps: float = 5.0, commission_bps: float = 10.0):
        self.slippage_bps = slippage_bps
        self.commission_bps = commission_bps
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.fills: List[Dict[str, Any]] = []

    def execute_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        order_type: str = "MARKET",
        signal_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simulate order fill with slippage and commission.
        """
        order_id = f"ORD-{symbol}-{uuid.uuid4().hex[:6].upper()}"
        fill_id = f"FILL-{symbol}-{uuid.uuid4().hex[:6].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Apply slippage model
        slippage_mult = 1.0 + (self.slippage_bps / 10000.0) if side == "BUY" else 1.0 - (self.slippage_bps / 10000.0)
        fill_price = price * slippage_mult
        gross_value = quantity * fill_price
        fee = gross_value * (self.commission_bps / 10000.0)
        net_value = gross_value + fee if side == "BUY" else gross_value - fee

        order_record = {
            "order_id": order_id,
            "fill_id": fill_id,
            "timestamp": now_iso,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "reference_price": round(price, 2),
            "fill_price": round(fill_price, 2),
            "slippage_bps": self.slippage_bps,
            "commission_fee": round(fee, 2),
            "gross_value": round(gross_value, 2),
            "net_value": round(net_value, 2),
            "status": "FILLED",
            "signal_id": signal_id or "SIG-MANUAL"
        }

        self.orders[order_id] = order_record
        self.fills.append(order_record)
        return order_record

    def get_orders(self) -> List[Dict[str, Any]]:
        return list(self.orders.values())

    def get_fills(self) -> List[Dict[str, Any]]:
        return self.fills
