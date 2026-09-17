"""
Paper Broker Implementation.
Adapts internal PaperExecutionEngine to implement standard BrokerInterface.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Any, Optional

from src.execution.broker.base import BrokerInterface, AccountInfo, PositionInfo, OrderBook
class PaperBroker(BrokerInterface):
    """Paper Broker Adapter for simulated paper trading execution."""

    def __init__(
        self,
        initial_capital: float = 100000.0,
        slippage_bps: float = 5.0,
        commission_bps: float = 10.0,
        account_id: str = "PAPER-ACCT-001"
    ):
        from src.realtime.execution.paper_execution import PaperExecutionEngine

        self.account_id = account_id
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self._connected = False
        self.execution_engine = PaperExecutionEngine(
            slippage_bps=slippage_bps, commission_bps=commission_bps
        )
        self.positions: Dict[str, PositionInfo] = {}
        self.latest_prices: Dict[str, float] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def is_connected(self) -> bool:
        return self._connected

    def get_account(self) -> AccountInfo:
        eq = self._calculate_equity()
        return AccountInfo(
            account_id=self.account_id,
            environment="PAPER",
            currency="USD",
            cash=round(self.cash, 2),
            equity=round(eq, 2),
            buying_power=round(self.cash, 2),
            margin_used=0.0,
            is_active=self._connected
        )

    def get_balance(self) -> Dict[str, float]:
        eq = self._calculate_equity()
        return {"cash": round(self.cash, 2), "equity": round(eq, 2)}

    def get_positions(self) -> Dict[str, PositionInfo]:
        return self.positions

    def update_market_price(self, symbol: str, price: float):
        """Update live market price snapshot for mark-to-market accounting."""
        self.latest_prices[symbol] = price
        if symbol in self.positions:
            pos = self.positions[symbol]
            pos.market_price = price
            pos.market_value = pos.quantity * price
            pos.unrealized_pnl = (price - pos.avg_price) * pos.quantity
            eq = self._calculate_equity()
            pos.weight = pos.market_value / eq if eq > 0 else 0.0

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        price = self.latest_prices.get(symbol, 150.0)
        return {
            "symbol": symbol,
            "bid": round(price * 0.9995, 2),
            "ask": round(price * 1.0005, 2),
            "last": round(price, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_order_book(self, symbol: str) -> Optional[OrderBook]:
        price = self.latest_prices.get(symbol, 150.0)
        return OrderBook(
            symbol=symbol,
            bids=[{"price": round(price * 0.999, 2), "size": 500}],
            asks=[{"price": round(price * 1.001, 2), "size": 500}]
        )

    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "DAY",
        signal_id: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self._connected:
            raise ConnectionError("PaperBroker is not connected!")

        price = limit_price or self.latest_prices.get(symbol, 150.0)
        order_record = self.execution_engine.execute_order(
            symbol=symbol,
            side=side.upper(),
            quantity=quantity,
            price=price,
            order_type=order_type,
            signal_id=signal_id
        )

        # Append broker tracking attributes
        order_record["broker_order_id"] = f"PB-{order_record['order_id']}"
        order_record["environment"] = "PAPER"
        order_record["idempotency_key"] = idempotency_key

        self.orders[order_record["order_id"]] = order_record
        self._update_position_from_fill(order_record)

        return order_record

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        if order_id in self.orders:
            self.orders[order_id]["status"] = "CANCELLED"
            return {"status": "CANCELLED", "order_id": order_id}
        return {"status": "NOT_FOUND", "order_id": order_id}

    def modify_order(self, order_id: str, quantity: Optional[float] = None, limit_price: Optional[float] = None) -> Dict[str, Any]:
        if order_id in self.orders:
            if quantity:
                self.orders[order_id]["quantity"] = quantity
            if limit_price:
                self.orders[order_id]["reference_price"] = limit_price
            return {"status": "MODIFIED", "order": self.orders[order_id]}
        return {"status": "NOT_FOUND", "order_id": order_id}

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return self.orders.get(order_id)

    def get_orders(self) -> List[Dict[str, Any]]:
        return list(self.orders.values())

    def get_fills(self) -> List[Dict[str, Any]]:
        return self.execution_engine.get_fills()

    def get_market_status(self) -> Dict[str, Any]:
        return {"status": "OPEN", "session": "REGULAR", "is_open": True}

    def _update_position_from_fill(self, fill: Dict[str, Any]):
        symbol = fill["symbol"]
        qty = fill["quantity"]
        side = fill["side"]
        fill_price = fill["fill_price"]
        net_val = fill["net_value"]

        if side == "BUY":
            self.cash -= net_val
            if symbol not in self.positions:
                self.positions[symbol] = PositionInfo(
                    symbol=symbol,
                    quantity=qty,
                    avg_price=fill_price,
                    market_price=fill_price,
                    market_value=qty * fill_price,
                    unrealized_pnl=0.0
                )
            else:
                pos = self.positions[symbol]
                tot_qty = pos.quantity + qty
                pos.avg_price = (pos.avg_price * pos.quantity + fill_price * qty) / tot_qty
                pos.quantity = tot_qty
                pos.market_price = fill_price
                pos.market_value = tot_qty * fill_price
        elif side == "SELL":
            self.cash += net_val
            if symbol in self.positions:
                pos = self.positions[symbol]
                realized = (fill_price - pos.avg_price) * min(qty, pos.quantity)
                pos.realized_pnl += realized
                rem_qty = pos.quantity - qty
                if rem_qty <= 0:
                    del self.positions[symbol]
                else:
                    pos.quantity = rem_qty
                    pos.market_value = rem_qty * fill_price

        eq = self._calculate_equity()
        for p in self.positions.values():
            p.weight = p.market_value / eq if eq > 0 else 0.0

    def _calculate_equity(self) -> float:
        pos_val = sum(p.market_value for p in self.positions.values())
        return self.cash + pos_val
