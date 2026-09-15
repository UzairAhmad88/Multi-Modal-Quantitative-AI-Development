from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

from src.backtesting.execution import execute_order, FillResult
from src.backtesting.metrics import compute_performance_metrics
from src.risk.risk_manager import RiskEngine
from src.utils.logger import get_logger

logger = get_logger("backtest_engine")


@dataclass
class BacktestConfig:
    initial_capital: float = 100000.0
    transaction_cost_bps: float = 10.0
    slippage_bps: float = 5.0
    rebalance_freq: str = "1D"
    max_position: float = 0.25
    max_sector_exposure: float = 0.40


class BacktestEngine:
    """Quantitative research backtester enforcing realistic execution timing, costs, and risk limits."""

    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig()
        self.risk_engine = RiskEngine(
            max_position=self.config.max_position,
            max_sector_exposure=self.config.max_sector_exposure
        )

    def run(
        self,
        market_data: pd.DataFrame,
        target_weights: pd.DataFrame,
        sector_map: Dict[str, str] | None = None
    ) -> Dict[str, Any]:
        """Run backtest simulation.

        Execution Timing Policy:
        - Signal and target weight generated at Close of day T.
        - Execution occurs at Open of day T+1 using Open price with slippage and fees.
        """
        # Ensure date sorting
        df_mkt = market_data.sort_values(["date", "ticker"]).copy()
        df_mkt["date"] = pd.to_datetime(df_mkt["date"], utc=True)
        dates = sorted(df_mkt["date"].unique())
        tickers = list(df_mkt["ticker"].unique())

        cash = self.config.initial_capital
        portfolio_shares: Dict[str, float] = {t: 0.0 for t in tickers}
        equity_history = []
        fill_history: List[FillResult] = []
        weight_history: List[pd.Series] = []

        # Pivot prices for fast daily lookup
        open_prices = df_mkt.pivot(index="date", columns="ticker", values="open").ffill().bfill()
        close_prices = df_mkt.pivot(index="date", columns="ticker", values="close").ffill().bfill()

        # Iterate through timeline bar-by-bar
        for i, current_date in enumerate(dates):
            # Current portfolio mark-to-market value at Open
            current_open = open_prices.loc[current_date]
            current_close = close_prices.loc[current_date]

            port_val_open = cash + sum(portfolio_shares[t] * current_open.get(t, 0.0) for t in tickers)

            # Rebalance execution if signals exist for previous close T-1
            if current_date in target_weights.index:
                raw_target = target_weights.loc[current_date]
                # Pass proposed portfolio through RISK GATE
                gated_weights, _ = self.risk_engine.validate_and_gate_portfolio(raw_target, sector_map)
                weight_history.append(gated_weights)

                # Execute orders across assets
                for ticker in tickers:
                    if ticker in gated_weights:
                        tgt_w = float(gated_weights[ticker])
                        open_p = float(current_open.get(ticker, 0.0))
                        if open_p > 0:
                            curr_s = portfolio_shares[ticker]
                            new_s, fill = execute_order(
                                ticker=ticker,
                                date=str(current_date),
                                target_weight=tgt_w,
                                current_shares=curr_s,
                                open_price=open_p,
                                portfolio_value=port_val_open,
                                transaction_cost_bps=self.config.transaction_cost_bps,
                                slippage_bps=self.config.slippage_bps
                            )
                            if fill.order.signal != "HOLD":
                                # Portfolio cash adjustment
                                delta_shares = new_s - curr_s
                                cost = (delta_shares * fill.fill_price) + fill.transaction_fee
                                cash -= cost
                                portfolio_shares[ticker] = new_s
                                fill_history.append(fill)

            # End of day Close mark-to-market accounting
            port_val_close = cash + sum(portfolio_shares[t] * current_close.get(t, 0.0) for t in tickers)
            equity_history.append(port_val_close)

        equity_series = pd.Series(equity_history, index=dates)
        metrics = compute_performance_metrics(equity_series, fill_history, weight_history)

        return {
            "equity_curve": equity_series,
            "metrics": metrics,
            "trade_logs": fill_history,
            "final_portfolio_value": equity_history[-1] if equity_history else self.config.initial_capital
        }
