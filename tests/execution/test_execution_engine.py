"""
Unit & Integration Tests for Phase 19 Execution Simulation & Market Microstructure OS.
"""

import pytest
from execution.trade_generator import TradeGenerator
from execution.orders.order import Order
from execution.orders.order_types import OrderType, OrderSide, TimeInForce
from execution.orders.order_status import OrderStatus
from execution.order_management.validation import OrderValidator
from execution.order_management.order_manager import OrderManager
from execution.fills.fill_engine import Fill, FillEngine
from execution.microstructure.order_book import OrderBook
from execution.slippage.slippage_engine import SlippageEngine
from execution.latency.latency_engine import LatencyEngine
from execution.liquidity.liquidity_engine import LiquidityEngine
from execution.market_impact.market_impact_engine import MarketImpactEngine
from execution.transaction_costs.fee_engine import FeeEngine
from execution.execution.algorithms.market import MarketExecutionAlgorithm
from execution.execution.algorithms.twap import TWAPExecutionAlgorithm
from execution.execution.algorithms.vwap import VWAPExecutionAlgorithm
from execution.execution.algorithms.pov import POVExecutionAlgorithm
from execution.accounting.portfolio_accounting import PortfolioAccounting
from execution.analytics.implementation_shortfall import ImplementationShortfall
from execution.manager import ExecutionManager


def test_trade_generator():
    gen = TradeGenerator(allow_fractional=True)
    curr_w = {"AAPL": 0.1, "MSFT": 0.2}
    targ_w = {"AAPL": 0.3, "MSFT": 0.0}
    prices = {"AAPL": 150.0, "MSFT": 300.0}

    trades = gen.generate_trades(curr_w, targ_w, prices, portfolio_value=100000.0)
    assert len(trades) == 2
    aapl_trade = next(t for t in trades if t["asset"] == "AAPL")
    msft_trade = next(t for t in trades if t["asset"] == "MSFT")

    assert aapl_trade["side"] == OrderSide.BUY
    assert aapl_trade["quantity"] == pytest.approx(133.3333, rel=1e-3)

    assert msft_trade["side"] == OrderSide.SELL
    assert msft_trade["quantity"] == pytest.approx(66.6666, rel=1e-3)


def test_order_validation():
    val = OrderValidator(max_order_value=100000.0, max_quantity=1000.0)

    o_valid = Order(asset="AAPL", side=OrderSide.BUY, quantity=100.0)
    ok, err = val.validate(o_valid, price=150.0)
    assert ok is True
    assert err is None

    o_invalid_qty = Order(asset="AAPL", side=OrderSide.BUY, quantity=-10.0)
    ok, err = val.validate(o_invalid_qty, price=150.0)
    assert ok is False
    assert "Non-positive" in err


def test_order_manager_lifecycle():
    mgr = OrderManager()
    o = Order(asset="AAPL", side=OrderSide.BUY, quantity=100.0)
    created = mgr.create_order(o, price=150.0)

    assert created.status == OrderStatus.SUBMITTED
    assert len(mgr.get_all_orders()) == 1

    updated = mgr.update_order_status(o.order_id, OrderStatus.FILLED, filled_qty=100.0, fill_price=150.0)
    assert updated.status == OrderStatus.FILLED
    assert updated.filled_quantity == 100.0


def test_slippage_directional_fairness():
    slip = SlippageEngine(model="fixed_bps", fixed_bps=10.0)  # 10 bps = 0.1%

    # BUY pays higher price
    res_buy = slip.calculate_execution_price(ref_price=100.0, side=OrderSide.BUY, quantity=100.0)
    assert res_buy["execution_price"] == 100.10

    # SELL receives lower price
    res_sell = slip.calculate_execution_price(ref_price=100.0, side=OrderSide.SELL, quantity=100.0)
    assert res_sell["execution_price"] == 99.90


def test_liquidity_cap_partial_fills():
    liq = LiquidityEngine(max_participation_rate=0.10)
    # Requested 1000 shares, market volume 2000 -> max fillable 200
    res = liq.evaluate_fill_capacity(requested_quantity=1000.0, market_volume=2000.0)

    assert res["filled_quantity"] == 200.0
    assert res["remaining_quantity"] == 800.0
    assert res["is_partial_fill"] is True


def test_execution_algorithms_slicing():
    o = Order(asset="AAPL", side=OrderSide.BUY, quantity=1000.0)

    twap = TWAPExecutionAlgorithm(num_intervals=5)
    twap_slices = twap.generate_slices(o)
    assert len(twap_slices) == 5
    assert sum(s.quantity for s in twap_slices) == pytest.approx(1000.0)

    vwap = VWAPExecutionAlgorithm()
    vwap_slices = vwap.generate_slices(o)
    assert len(vwap_slices) == 5
    assert sum(s.quantity for s in vwap_slices) == pytest.approx(1000.0)

    pov = POVExecutionAlgorithm(target_participation_rate=0.10, interval_volume=2000.0)
    pov_slices = pov.generate_slices(o)
    assert len(pov_slices) == 5
    assert all(s.quantity == 200.0 for s in pov_slices)


def test_portfolio_accounting():
    acct = PortfolioAccounting(initial_cash=100000.0)
    fill_buy = Fill(
        fill_id="FILL-001",
        order_id="ORD-001",
        asset="AAPL",
        side=OrderSide.BUY,
        quantity=100.0,
        fill_price=150.0,
        timestamp="2026-09-16T12:00:00Z",
        fees=15.0
    )
    acct.process_fill(fill_buy)

    assert acct.cash == 100000.0 - (100.0 * 150.0 + 15.0)
    assert acct.positions["AAPL"]["quantity"] == 100.0
    assert acct.positions["AAPL"]["avg_price"] == 150.0

    fill_sell = Fill(
        fill_id="FILL-002",
        order_id="ORD-002",
        asset="AAPL",
        side=OrderSide.SELL,
        quantity=50.0,
        fill_price=160.0,
        timestamp="2026-09-16T12:05:00Z",
        fees=10.0
    )
    acct.process_fill(fill_sell)

    assert acct.positions["AAPL"]["quantity"] == 50.0
    assert acct.realized_pnl == pytest.approx((160.0 - 150.0) * 50.0 - 10.0)


def test_execution_manager_pipeline():
    mgr = ExecutionManager(initial_cash=100000.0, algorithm="TWAP")
    curr_w = {"AAPL": 0.0}
    targ_w = {"AAPL": 0.2}
    snaps = {"AAPL": {"close": 150.0, "volume": 500000.0, "adv": 1000000.0, "volatility": 0.015}}

    res = mgr.run_execution(current_weights=curr_w, target_weights=targ_w, market_snapshots=snaps)

    assert res["execution_id"].startswith("EXEC-")
    assert res["algorithm"] == "TWAP"
    assert res["total_trades_generated"] == 1
    assert res["child_orders_count"] == 5
    assert len(res["fills"]) == 5
    assert res["validation"]["valid"] is True
