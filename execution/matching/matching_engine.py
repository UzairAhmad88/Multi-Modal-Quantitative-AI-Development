"""
Matching Engine: Simulates market order fill prices and limit order trigger logic against OHLCV and spread snapshots.
"""

from typing import Dict, Any, Tuple, Optional
from execution.orders.order import Order
from execution.orders.order_types import OrderType, OrderSide
from execution.microstructure.order_book import OrderBook


class MatchingEngine:
    """Matches orders against market snapshot data."""

    def __init__(self, default_spread_bps: float = 2.0):
        self.default_spread_bps = default_spread_bps

    def match_order(
        self,
        order: Order,
        market_snapshot: Dict[str, Any],
        order_book: Optional[OrderBook] = None
    ) -> Tuple[bool, float, str]:
        """Determines fill eligibility and base fill price prior to slippage/impact."""
        close_price = market_snapshot.get("close", market_snapshot.get("price", 100.0))
        high_price = market_snapshot.get("high", close_price * 1.01)
        low_price = market_snapshot.get("low", close_price * 0.99)
        open_price = market_snapshot.get("open", close_price)

        if order_book and order_book.best_bid and order_book.best_ask:
            bid = order_book.best_bid
            ask = order_book.best_ask
        else:
            half_spread = (close_price * (self.default_spread_bps / 10000.0)) / 2.0
            bid = close_price - half_spread
            ask = close_price + half_spread

        if order.order_type == OrderType.MARKET:
            base_price = ask if order.side in (OrderSide.BUY, OrderSide.COVER) else bid
            return True, base_price, "MARKET_MATCH"

        elif order.order_type == OrderType.LIMIT:
            limit = order.limit_price or close_price
            if order.side in (OrderSide.BUY, OrderSide.COVER):
                if low_price <= limit:
                    fill_price = min(limit, ask)
                    return True, fill_price, "LIMIT_BUY_MATCH"
                return False, 0.0, "LIMIT_PRICE_UNREACHED"
            else:
                if high_price >= limit:
                    fill_price = max(limit, bid)
                    return True, fill_price, "LIMIT_SELL_MATCH"
                return False, 0.0, "LIMIT_PRICE_UNREACHED"

        elif order.order_type == OrderType.STOP:
            stop = order.stop_price or close_price
            if order.side in (OrderSide.BUY, OrderSide.COVER):
                if high_price >= stop:
                    return True, ask, "STOP_BUY_TRIGGERED"
                return False, 0.0, "STOP_PRICE_UNREACHED"
            else:
                if low_price <= stop:
                    return True, bid, "STOP_SELL_TRIGGERED"
                return False, 0.0, "STOP_PRICE_UNREACHED"

        return False, 0.0, "UNSUPPORTED_ORDER_TYPE"
