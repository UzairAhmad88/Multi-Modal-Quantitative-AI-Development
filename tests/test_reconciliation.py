"""
Unit tests for Position and Account Reconciliation Engine.
"""

import pytest
from src.execution.broker.paper import PaperBroker
from src.execution.reconciliation.engine import ReconciliationEngine


def test_reconciliation_pass_clean():
    broker = PaperBroker(initial_capital=100000.0)
    broker.connect()
    broker.update_market_price("AAPL", 150.0)
    broker.submit_order("AAPL", "BUY", 10.0, limit_price=150.0)

    acc = broker.get_account()
    pos = broker.get_positions()
    local_pos = {sym: {"quantity": p.quantity} for sym, p in pos.items()}

    engine = ReconciliationEngine()
    res = engine.reconcile(broker=broker, local_cash=acc.cash, local_positions=local_pos)

    assert res.is_reconciled is True
    assert len(res.mismatches) == 0
    assert res.status_summary == "RECONCILED_OK"


def test_reconciliation_detects_cash_mismatch():
    broker = PaperBroker(initial_capital=100000.0)
    broker.connect()

    engine = ReconciliationEngine()
    # Provide incorrect local cash
    res = engine.reconcile(broker=broker, local_cash=95000.0, local_positions={})

    assert res.is_reconciled is False
    assert len(res.mismatches) == 1
    assert res.mismatches[0]["type"] == "CASH_MISMATCH"


def test_reconciliation_detects_position_mismatch():
    broker = PaperBroker(initial_capital=100000.0)
    broker.connect()
    broker.update_market_price("AAPL", 150.0)
    broker.submit_order("AAPL", "BUY", 10.0, limit_price=150.0)

    acc = broker.get_account()

    engine = ReconciliationEngine()
    # Provide local position as 5.0 instead of 10.0
    res = engine.reconcile(broker=broker, local_cash=acc.cash, local_positions={"AAPL": {"quantity": 5.0}})

    assert res.is_reconciled is False
    assert len(res.mismatches) == 1
    assert res.mismatches[0]["type"] == "POSITION_MISMATCH"
    assert res.mismatches[0]["symbol"] == "AAPL"
