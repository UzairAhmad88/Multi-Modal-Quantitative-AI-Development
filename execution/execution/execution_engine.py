"""
Execution Engine: Coordinates order matching, liquidity caps, slippage penalties, market impact, latency timing, and fill generation.
"""

from typing import Dict, Any, List, Optional
from execution.orders.order import Order
from execution.orders.order_status import OrderStatus
from execution.order_management.order_manager import OrderManager
from execution.matching.matching_engine import MatchingEngine
from execution.liquidity.liquidity_engine import LiquidityEngine
from execution.slippage.slippage_engine import SlippageEngine
from execution.market_impact.market_impact_engine import MarketImpactEngine
from execution.latency.latency_engine import LatencyEngine
from execution.fills.fill_engine import Fill, FillEngine
from execution.transaction_costs.fee_engine import FeeEngine


class ExecutionEngine:
    """Core Execution Simulation Processor."""

    def __init__(
        self,
        order_manager: Optional[OrderManager] = None,
        matching_engine: Optional[MatchingEngine] = None,
        liquidity_engine: Optional[LiquidityEngine] = None,
        slippage_engine: Optional[SlippageEngine] = None,
        impact_engine: Optional[MarketImpactEngine] = None,
        latency_engine: Optional[LatencyEngine] = None,
        fill_engine: Optional[FillEngine] = None,
        fee_engine: Optional[FeeEngine] = None
    ):
        self.order_manager = order_manager or OrderManager()
        self.matching_engine = matching_engine or MatchingEngine()
        self.liquidity_engine = liquidity_engine or LiquidityEngine()
        self.slippage_engine = slippage_engine or SlippageEngine()
        self.impact_engine = impact_engine or MarketImpactEngine()
        self.latency_engine = latency_engine or LatencyEngine()
        self.fill_engine = fill_engine or FillEngine()
        self.fee_engine = fee_engine or FeeEngine()

    def execute_order(
        self,
        order: Order,
        market_snapshot: Dict[str, Any]
    ) -> List[Fill]:
        """Executes a single order against market snapshot and returns fill records."""
        if order.status not in (OrderStatus.SUBMITTED, OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED):
            return []

        matched, base_price, reason = self.matching_engine.match_order(order, market_snapshot)
        if not matched:
            return []

        vol = market_snapshot.get("volume", 100000.0)
        adv = market_snapshot.get("adv", 1000000.0)
        volatility = market_snapshot.get("volatility", 0.02)

        # 1. Liquidity capacity evaluation
        liq_res = self.liquidity_engine.evaluate_fill_capacity(order.remaining_quantity, market_volume=vol, adv=adv)
        fill_qty = liq_res["filled_quantity"]

        if fill_qty <= 0:
            return []

        # 2. Slippage & Market Impact
        slip_res = self.slippage_engine.calculate_execution_price(
            ref_price=base_price, side=order.side, quantity=fill_qty, volume=vol, volatility=volatility
        )
        impact_res = self.impact_engine.calculate_impact(
            order_quantity=fill_qty, price=base_price, adv=adv, volatility=volatility
        )

        final_price = slip_res["execution_price"] + (impact_res["impact_cost"] / fill_qty if fill_qty > 0 else 0.0)
        final_price = round(final_price, 4)

        # 3. Fees & Latency
        fees_res = self.fee_engine.calculate_fees(fill_qty * final_price)
        latency_info = self.latency_engine.compute_timestamps(base_timestamp=order.timestamp)

        # 4. Fill generation
        fill = self.fill_engine.create_fill(
            order=order,
            fill_qty=fill_qty,
            fill_price=final_price,
            timestamp=latency_info["fill_timestamp"],
            fees=fees_res["total_fee"],
            slippage=slip_res["slippage_cost"],
            latency_ms=latency_info["total_latency_ms"]
        )

        # 5. OMS status update
        new_status = OrderStatus.FILLED if order.remaining_quantity - fill_qty <= 1e-6 else OrderStatus.PARTIALLY_FILLED
        self.order_manager.update_order_status(order.order_id, status=new_status, filled_qty=fill_qty, fill_price=final_price)

        return [fill]
