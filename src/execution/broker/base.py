"""
Base Abstract Broker Interface Definition.
Enforces standard operations across Paper, Sandbox, Shadow, and Real Broker Adapters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


@dataclass
class AccountInfo:
    account_id: str
    environment: str
    currency: str = "USD"
    cash: float = 100000.0
    equity: float = 100000.0
    buying_power: float = 100000.0
    margin_used: float = 0.0
    is_active: bool = True
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class PositionInfo:
    symbol: str
    quantity: float
    avg_price: float
    market_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    weight: float = 0.0


@dataclass
class OrderBook:
    symbol: str
    bids: List[Dict[str, float]] = field(default_factory=list)  # [{"price": 150.0, "size": 100}]
    asks: List[Dict[str, float]] = field(default_factory=list)  # [{"price": 150.05, "size": 100}]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BrokerInterface(ABC):
    """
    Abstract Base Class for all Broker Integrations.
    Ensures complete decoupling of trading strategy and risk models from the execution venue.
    """

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to broker API."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect safely from broker API."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check connection status."""
        pass

    @abstractmethod
    def get_account(self) -> AccountInfo:
        """Fetch current account balances and buying power."""
        pass

    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """Fetch cash and equity breakdown."""
        pass

    @abstractmethod
    def get_positions(self) -> Dict[str, PositionInfo]:
        """Fetch active positions dictionary keyed by ticker symbol."""
        pass

    @abstractmethod
    def get_quote(self) -> Dict[str, Any]:
        """Fetch latest price quote for a symbol."""
        pass

    @abstractmethod
    def get_order_book(self) -> Optional[OrderBook]:
        """Fetch level 2 order book if supported."""
        pass

    @abstractmethod
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
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submit order to broker and return order record."""
        pass

    @abstractmethod
    def cancel_order(self) -> Dict[str, Any]:
        """Cancel an open order by order_id."""
        pass

    @abstractmethod
    def modify_order(self) -> Dict[str, Any]:
        """Modify open order parameters."""
        pass

    @abstractmethod
    def get_order(self) -> Optional[Dict[str, Any]]:
        """Fetch specific order details by ID."""
        pass

    @abstractmethod
    def get_orders(self) -> List[Dict[str, Any]]:
        """Fetch all orders for session or account."""
        pass

    @abstractmethod
    def get_fills(self) -> List[Dict[str, Any]]:
        """Fetch all fill executions."""
        pass

    @abstractmethod
    def get_market_status(self) -> Dict[str, Any]:
        """Check exchange session status (OPEN, CLOSED, PRE_MARKET, POST_MARKET)."""
        pass
