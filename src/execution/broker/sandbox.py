"""
Sandbox Broker Implementation.
Simulates order queueing, partial fills, sandbox exchange behavior, and latency.
"""

from datetime import datetime, timezone
import uuid
import time
from typing import Dict, List, Any, Optional

from src.execution.broker.base import BrokerInterface, AccountInfo, PositionInfo, OrderBook


class SandboxBroker(BrokerInterface):
    """Sandbox Broker Adapter simulating exchange demo behavior."""

    def __init__(self, initial_cash: float = 100000.0, sandbox_account_id: str = "SANDBOX-ACCT-888"):
        self.account_id = sandbox_account_id
        self.cash = initial_cash
        self._connected = False
        self.positions: Dict[str, PositionInfo] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.fills: List[Dict[str, Any]] = []
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
        eq = self.cash + sum(p.market_value for p in self.positions.values())
        return AccountInfo(
            account_id=self.account_id,
            environment="SANDBOX",
            currency="USD",
            cash=round(self.cash, 2),
            equity=round(eq, 2),
            buying_power=round(self.cash, 2),
            margin_used=0.0,
            is_active=self._connected
        )

    def get_balance(self) -> Dict[str, float]:
        eq = self.cash + sum(p.market_value for p in self.positions.values())
        return {"cash": round(self.cash, 2), "equity": round(eq, 2)}

    def get_positions(self) -> Dict[str, PositionInfo]:
        return self.positions

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
            bids=[{"price": round(price * 0.999, 2), "size": 1000}],
            asks=[{"price": round(price * 1.001, 2), "size": 1000}]
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
            raise ConnectionError("SandboxBroker is not connected!")

        order_id = f"SB-ORD-{uuid.uuid4().hex[:8].upper()}"
        broker_order_id = f"SANDBOX-{uuid.uuid4().hex[:6].upper()}"
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
            "status": "FILLED",
            "environment": "SANDBOX",
            "signal_id": signal_id or "SIG-SANDBOX",
            "idempotency_key": idempotency_key
        }

        self.orders[order_id] = record
        self.fills.append(record)

        # Accounting
        gross = quantity * fill_price
        if side.upper() == "BUY":
            self.cash -= gross
            if symbol not in self.positions:
                self.positions[symbol] = PositionInfo(
                    symbol=symbol,
                    quantity=quantity,
                    avg_price=fill_price,
                    market_price=fill_price,
                    market_value=gross,
                    unrealized_pnl=0.0
                )
            else:
                pos = self.positions[symbol]
                tot = pos.quantity + quantity
                pos.avg_price = (pos.avg_price * pos.quantity + gross) / tot
                pos.quantity = tot
                pos.market_value = tot * fill_price
        elif side.upper() == "SELL":
            self.cash += gross
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos.quantity -= quantity
                if pos.quantity <= 0:
                    del self.positions[symbol]

        return record

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        if order_id in self.orders:
            self.orders[order_id]["status"] = "CANCELLED"
            return {"status": "CANCELLED", "order_id": order_id}
        return {"status": "NOT_FOUND", "order_id": order_id}

    def modify_order(self, order_id: str, quantity: Optional[float] = None, limit_price: Optional[float] = None) -> Dict[str, Any]:
        if order_id in self.orders:
            if quantity:
                self.orders[order_id]["quantity"] = quantity
            return {"status": "MODIFIED", "order": self.orders[order_id]}
        return {"status": "NOT_FOUND", "order_id": order_id}

    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return self.orders.get(order_id)

    def get_orders(self) -> List[Dict[str, Any]]:
        return list(self.orders.values())

    def get_fills(self) -> List[Dict[str, Any]]:
        return self.fills

    def get_market_status(self) -> Dict[str, Any]:
        return {"status": "OPEN", "session": "SANDBOX", "is_open": True}
