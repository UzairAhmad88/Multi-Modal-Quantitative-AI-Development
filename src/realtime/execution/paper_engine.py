"""
Paper Execution Engine Module
Simulates order fills, slippage, transaction costs, and latency delays across order lifecycles.
"""

from datetime import datetime, timezone
import uuid
import time
from typing import Dict, List, Any, Optional, Tuple


class PaperExecutionEngine:
    """Quantitative Paper Order Execution & Fill Simulation Engine."""

    def __init__(
        self,
        default_cost_bps: float = 10.0,
        default_slippage_bps: float = 5.0,
        simulated_latency_ms: int = 50,
    ):
        self.cost_bps = default_cost_bps
        self.slippage_bps = default_slippage_bps
        self.latency_ms = simulated_latency_ms

        self.orders: Dict[str, Dict[str, Any]] = {}
        self.fills: List[Dict[str, Any]] = []

    def create_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        limit_price: Optional[float] = None,
        strategy_id: str = "MULTI_MODAL_AI",
    ) -> Dict[str, Any]:
        """
        Create a new paper order in CREATED state.
        """
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        now_utc = datetime.now(timezone.utc).isoformat()

        order = {
            "order_id": order_id,
            "timestamp": now_utc,
            "symbol": symbol.upper(),
            "side": side.upper(),
            "quantity": quantity,
            "order_type": order_type.upper(),
            "limit_price": limit_price,
            "status": "CREATED",
            "strategy_id": strategy_id,
            "filled_quantity": 0.0,
            "filled_price": 0.0,
            "commission": 0.0,
            "slippage": 0.0,
        }
        self.orders[order_id] = order
        return order

    def execute_order(
        self, order_id: str, market_price: float, is_approved: bool = True, rejection_reason: str = ""
    ) -> Dict[str, Any]:
        """
        Process order through VALIDATING -> APPROVED -> SUBMITTED -> FILLED or REJECTED.
        """
        if order_id not in self.orders:
            raise ValueError(f"Order ID {order_id} not found")

        order = self.orders[order_id]

        if not is_approved:
            order["status"] = "REJECTED"
            order["rejection_reason"] = rejection_reason
            return order

        order["status"] = "VALIDATING"
        order["status"] = "APPROVED"

        # Simulate latency delay if configured
        if self.latency_ms > 0:
            time.sleep(min(0.05, self.latency_ms / 1000.0))

        order["status"] = "SUBMITTED"

        # Compute slippage & fill price
        side_multiplier = 1.0 if order["side"] == "BUY" else -1.0
        slippage_pct = (self.slippage_bps / 10000.0) * side_multiplier
        fill_price = round(market_price * (1.0 + slippage_pct), 2)

        traded_value = order["quantity"] * fill_price
        commission = round(traded_value * (self.cost_bps / 10000.0), 2)
        slippage_cost = round(traded_value * (self.slippage_bps / 10000.0), 2)

        order["status"] = "FILLED"
        order["filled_quantity"] = order["quantity"]
        order["filled_price"] = fill_price
        order["commission"] = commission
        order["slippage"] = slippage_cost
        order["fill_timestamp"] = datetime.now(timezone.utc).isoformat()

        fill_record = {
            "fill_id": f"FILL-{uuid.uuid4().hex[:8].upper()}",
            "order_id": order_id,
            "symbol": order["symbol"],
            "side": order["side"],
            "quantity": order["quantity"],
            "fill_price": fill_price,
            "traded_value": traded_value,
            "commission": commission,
            "slippage_cost": slippage_cost,
            "timestamp": order["fill_timestamp"],
        }
        self.fills.append(fill_record)

        return order
