"""
Shadow Broker Adapter.
Executes Shadow Trading Mode (LIVE DATA + LIVE MODEL + LIVE SIGNALS -> ZERO live orders dispatched).
Logs all hypothetical decisions, orders, and fills for out-of-sample execution auditing.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Any, Optional

from src.execution.broker.base import BrokerInterface, AccountInfo, PositionInfo, OrderBook


class ShadowBroker(BrokerInterface):
    """Shadow Broker Adapter for non-executing hypothetical paper trade verification."""

    def __init__(self, initial_cash: float = 100000.0, account_id: str = "SHADOW-ACCT-999"):
        self.account_id = account_id
        self.cash = initial_cash
        self._connected = False
        self.hypothetical_positions: Dict[str, PositionInfo] = {}
        self.hypothetical_orders: Dict[str, Dict[str, Any]] = {}
        self.hypothetical_fills: List[Dict[str, Any]] = []
        self.latest_prices: Dict[str, float] = {}

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def is_connected(self) -> bool:
        return self._connected

    def get_account(self) -> AccountInfo:
        eq = self.cash + sum(p.market_value for p in self.hypothetical_positions.values())
        return AccountInfo(
            account_id=self.account_id,
            environment="SHADOW",
            currency="USD",
            cash=round(self.cash, 2),
            equity=round(eq, 2),
            buying_power=round(self.cash, 2),
            margin_used=0.0,
            is_active=self._connected
        )

    def get_balance(self) -> Dict[str, float]:
        eq = self.cash + sum(p.market_value for p in self.hypothetical_positions.values())
        return {"cash": round(self.cash, 2), "equity": round(eq, 2)}

    def get_positions(self) -> Dict[str, PositionInfo]:
        return self.hypothetical_positions

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        price = self.latest_prices.get(symbol, 150.0)
        return {
            "symbol": symbol,
            "bid": round(price * 0.999, 2),
            "ask": round(price * 1.001, 2),
            "last": round(price, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_order_book(self, symbol: str) -> Optional[OrderBook]:
        price = self.latest_prices.get(symbol, 150.0)
        return OrderBook(
            symbol=symbol,
            bids=[{"price": round(price * 0.999, 2), "size": 100}],
            asks=[{"price": round(price * 1.001, 2), "size": 100}]
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
        """
        Record hypothetical order in Shadow Mode without dispatching to any exchange or broker.
        """
        order_id = f"SHADOW-ORD-{uuid.uuid4().hex[:8].upper()}"
        broker_order_id = f"SHADOW-HYPO-{uuid.uuid4().hex[:6].upper()}"
        fill_price = limit_price or self.latest_prices.get(symbol, 150.0)

        record = {
            "order_id": order_id,
            "broker_order_id": broker_order_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol,
            "side": side.upper(),
            "quantity": quantity,
            "filled_quantity": quantity,
            "order_type": order_type,
            "fill_price": round(fill_price, 2),
            "status": "HYPOTHETICAL_FILL",
            "environment": "SHADOW",
            "is_hypothetical": True,
            "signal_id": signal_id or "SIG-SHADOW",
            "idempotency_key": idempotency_key
        }

        self.hypothetical_orders[order_id] = record
        self.hypothetical_fills.append(record)

        # Update internal hypothetical positions
        gross = quantity * fill_price
        if side.upper() == "BUY":
            self.cash -= gross
            if symbol not in self.hypothetical_positions:
                self.hypothetical_positions[symbol] = PositionInfo(
                    symbol=symbol,
                    quantity=quantity,
                    avg_price=fill_price,
                    market_price=fill_price,
                    market_value=gross,
                    unrealized_pnl=0.0
                )
            else:
                pos = self.hypothetical_positions[symbol]
                tot = pos.quantity + quantity
                pos.avg_price = (pos.avg_price * pos.quantity + gross) / tot
                pos.quantity = tot
                pos.market_value = tot * fill_price
        elif side.upper() == "SELL":
            self.cash += gross
            if symbol in self.hypothetical_positions:
                pos = self.hypothetical_positions[symbol]
                pos.quantity -= quantity
                if pos.quantity <= 0:
                    del self.hypothetical_positions[symbol]

        return record

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        if order_id in self.hypothetical_orders:
            self.hypothetical_orders[order_id]["status"] = "CANCELLED"
            return {"status": "CANCELLED", "order_id": order_id}
        return {"status": "NOT_FOUND", "order_id": order_id}

    def modify_order(self, order_id: str, quantity: Optional[float] = None, limit_price: Optional[float] = None) -> Dict[str, Any]:
        if order_id in self.hypothetical_orders:
            if quantity:
                self.hypothetical_orders[order_id]["quantity"] = quantity
            return {"status": "MODIFIED", "order": self.hypothetical_orders[order_id]}
        return {"status": "NOT_FOUND", "order_id": order_id}

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return self.hypothetical_orders.get(order_id)

    def get_orders(self) -> List[Dict[str, Any]]:
        return list(self.hypothetical_orders.values())

    def get_fills(self) -> List[Dict[str, Any]]:
        return self.hypothetical_fills

    def get_market_status(self) -> Dict[str, Any]:
        return {"status": "OPEN", "session": "SHADOW_SIMULATION", "is_open": True}
