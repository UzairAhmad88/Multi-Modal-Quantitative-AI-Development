from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Any
import pandas as pd


@dataclass
class TradeOrder:
    ticker: str
    date: str
    signal: str
    target_weight: float
    execute_price: float
    shares: float
    cost_basis: float


@dataclass
class FillResult:
    order: TradeOrder
    fill_price: float
    slippage_cost: float
    transaction_fee: float
    net_notional: float


def execute_order(
    ticker: str,
    date: str,
    target_weight: float,
    current_shares: float,
    open_price: float,
    portfolio_value: float,
    transaction_cost_bps: float = 10.0,
    slippage_bps: float = 5.0
) -> Tuple[float, FillResult]:
    """Executes order at next bar open price with realistic slippage and fee accounting.

    Returns:
        (new_shares, FillResult)
    """
    target_notional = portfolio_value * target_weight
    current_notional = current_shares * open_price
    trade_notional = target_notional - current_notional

    if abs(trade_notional) < 1.0:  # Ignore trivial sub-dollar rebalances
        order = TradeOrder(ticker, str(date), "HOLD", target_weight, open_price, current_shares, current_notional)
        return current_shares, FillResult(order, open_price, 0.0, 0.0, current_notional)

    # Apply slippage: Buys execute slightly higher, Sells execute slightly lower
    slippage_pct = (slippage_bps / 10000.0)
    if trade_notional > 0:
        fill_price = open_price * (1.0 + slippage_pct)
        signal = "BUY"
    else:
        fill_price = open_price * (1.0 - slippage_pct)
        signal = "SELL"

    fee = abs(trade_notional) * (transaction_cost_bps / 10000.0)
    slippage_cost = abs(trade_notional) * slippage_pct

    delta_shares = trade_notional / fill_price
    new_shares = current_shares + delta_shares

    order = TradeOrder(ticker, str(date), signal, target_weight, fill_price, new_shares, abs(trade_notional))
    result = FillResult(order, fill_price, slippage_cost, fee, abs(trade_notional))

    return new_shares, result
