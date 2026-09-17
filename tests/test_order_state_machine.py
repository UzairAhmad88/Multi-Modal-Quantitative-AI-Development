"""
Unit tests for Order State Machine and Idempotency Tracking.
"""

import pytest
from src.execution.orders.state_machine import OrderStateMachine, OrderState
from src.execution.orders.order_lineage import LineageTracker, OrderLineageRecord
from execution.order_management.order_manager import OrderManager
from execution.orders.order import Order
from execution.orders.order_types import OrderSide, OrderType


def test_order_state_machine_valid_transitions():
    assert OrderStateMachine.can_transition(OrderState.CREATED, OrderState.VALIDATING) is True
    assert OrderStateMachine.can_transition(OrderState.VALIDATING, OrderState.APPROVED) is True
    assert OrderStateMachine.can_transition(OrderState.APPROVED, OrderState.SUBMITTED) is True
    assert OrderStateMachine.can_transition(OrderState.SUBMITTED, OrderState.FILLED) is True


def test_order_state_machine_invalid_transition_raises():
    assert OrderStateMachine.can_transition(OrderState.CREATED, OrderState.FILLED) is False
    with pytest.raises(ValueError):
        OrderStateMachine.validate_transition(OrderState.CREATED, OrderState.FILLED)


def test_order_manager_idempotency_protection():
    oms = OrderManager()
    order1 = Order(asset="AAPL", side=OrderSide.BUY, quantity=10.0, order_type=OrderType.MARKET)
    order2 = Order(asset="AAPL", side=OrderSide.BUY, quantity=10.0, order_type=OrderType.MARKET)

    res1 = oms.create_order(order1, price=150.0, idempotency_key="SIG-KEY-100")
    assert res1.status.value == "SUBMITTED"

    res2 = oms.create_order(order2, price=150.0, idempotency_key="SIG-KEY-100")
    assert res2.status.value == "REJECTED"
    assert "DUPLICATE_ORDER_BLOCKED" in res2.rejection_reason


def test_lineage_tracker_provenance():
    tracker = LineageTracker()
    rec = OrderLineageRecord(
        internal_order_id="ORD-101",
        signal_id="SIG-999",
        model_id="RF_MODEL",
        model_version="v1.0",
        environment="PAPER",
        symbol="AAPL",
        side="BUY",
        quantity=10.0,
        alpha_score=0.75
    )
    tracker.register_lineage(rec)

    tracker.update_broker_fill("ORD-101", broker_order_id="PB-101", fill_id="FILL-001", fill_price=150.50, filled_qty=10.0)

    fetched = tracker.get_lineage("ORD-101")
    assert fetched["broker_order_id"] == "PB-101"
    assert fetched["fill_price"] == 150.50
    assert fetched["status"] == "FILLED"
