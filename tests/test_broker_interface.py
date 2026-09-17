"""
Unit tests for Broker Interface Abstraction Layer.
Tests PaperBroker, SandboxBroker, ShadowBroker, and AlpacaBrokerAdapter.
"""

import pytest
from src.execution.broker.paper import PaperBroker
from src.execution.broker.sandbox import SandboxBroker
from src.execution.broker.adapters.shadow import ShadowBroker
from src.execution.broker.adapters.alpaca_adapter import AlpacaBrokerAdapter


def test_paper_broker_lifecycle():
    broker = PaperBroker(initial_capital=100000.0)
    assert broker.connect() is True
    assert broker.is_connected() is True

    acc = broker.get_account()
    assert acc.environment == "PAPER"
    assert acc.cash == 100000.0

    broker.update_market_price("AAPL", 150.0)
    order = broker.submit_order(symbol="AAPL", side="BUY", quantity=10.0, order_type="MARKET", signal_id="SIG-001")
    assert order["status"] == "FILLED"
    assert order["quantity"] == 10.0
    assert order["signal_id"] == "SIG-001"

    positions = broker.get_positions()
    assert "AAPL" in positions
    assert positions["AAPL"].quantity == 10.0

    assert broker.disconnect() is True
    assert broker.is_connected() is False


def test_sandbox_broker_lifecycle():
    broker = SandboxBroker(initial_cash=50000.0)
    broker.connect()
    assert broker.is_connected() is True

    acc = broker.get_account()
    assert acc.environment == "SANDBOX"
    assert acc.cash == 50000.0

    order = broker.submit_order(symbol="MSFT", side="BUY", quantity=5.0, limit_price=400.0)
    assert order["status"] == "FILLED"
    assert order["environment"] == "SANDBOX"

    positions = broker.get_positions()
    assert "MSFT" in positions
    assert positions["MSFT"].quantity == 5.0


def test_shadow_broker_hypothetical_orders():
    broker = ShadowBroker(initial_cash=100000.0)
    broker.connect()

    acc = broker.get_account()
    assert acc.environment == "SHADOW"

    order = broker.submit_order(symbol="NVDA", side="BUY", quantity=20.0, limit_price=120.0)
    assert order["status"] == "HYPOTHETICAL_FILL"
    assert order["is_hypothetical"] is True

    fills = broker.get_fills()
    assert len(fills) == 1
    assert fills[0]["symbol"] == "NVDA"


def test_alpaca_broker_adapter_unconnected_guard():
    adapter = AlpacaBrokerAdapter(paper=True)
    # Without keys, connect returns False
    assert adapter.connect() is False

    with pytest.raises(ConnectionError):
        adapter.submit_order(symbol="AAPL", side="BUY", quantity=10.0)
