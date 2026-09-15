from __future__ import annotations
from typing import Dict, Any
import numpy as np
import pandas as pd


def total_return(equity: pd.Series) -> float:
    if len(equity) < 2 or equity.iloc[0] == 0:
        return 0.0
    return float(equity.iloc[-1] / equity.iloc[0] - 1.0)


def cagr(equity: pd.Series, periods_per_year: int = 252) -> float:
    if len(equity) < 2 or equity.iloc[0] <= 0:
        return 0.0
    years = len(equity) / periods_per_year
    if years <= 0:
        return 0.0
    return float((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / years) - 1.0)


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods: int = 252) -> float:
    excess = returns - (risk_free_rate / periods)
    std = excess.std()
    if std <= 1e-8 or np.isnan(std):
        return 0.0
    return float(np.sqrt(periods) * excess.mean() / std)


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods: int = 252) -> float:
    excess = returns - (risk_free_rate / periods)
    downside = excess[excess < 0]
    downside_std = downside.std()
    if downside_std <= 1e-8 or np.isnan(downside_std):
        return 0.0
    return float(np.sqrt(periods) * excess.mean() / downside_std)


def calmar_ratio(equity: pd.Series, periods_per_year: int = 252) -> float:
    c = cagr(equity, periods_per_year)
    from src.risk.drawdown import max_drawdown
    mdd = abs(max_drawdown(equity))
    if mdd <= 1e-8:
        return 0.0
    return float(c / mdd)


def compute_performance_metrics(
    equity_series: pd.Series,
    trade_logs: list[Any] | None = None,
    rebalance_weights: list[pd.Series] | None = None
) -> Dict[str, Any]:
    """Compute comprehensive quantitative research performance report."""
    returns = equity_series.pct_change().dropna()
    tot_ret = total_return(equity_series)
    ann_cagr = cagr(equity_series)
    vol = float(returns.std() * np.sqrt(252))
    sh = sharpe_ratio(returns)
    sort = sortino_ratio(returns)
    cal = calmar_ratio(equity_series)

    from src.risk.drawdown import max_drawdown
    mdd = max_drawdown(equity_series)

    # Win rate and profit factor from daily returns
    pos_ret = returns[returns > 0]
    neg_ret = returns[returns < 0]
    win_rate = float(len(pos_ret) / max(1, len(returns)))
    profit_factor = float(pos_ret.sum() / abs(neg_ret.sum())) if len(neg_ret) > 0 and neg_ret.sum() != 0 else 1.0

    # Calculate portfolio turnover if weights provided
    turnover = 0.0
    if rebalance_weights and len(rebalance_weights) > 1:
        diffs = [abs(rebalance_weights[i] - rebalance_weights[i-1]).sum() for i in range(1, len(rebalance_weights))]
        turnover = float(np.mean(diffs))

    return {
        "total_return": round(tot_ret, 4),
        "cagr": round(ann_cagr, 4),
        "annualized_volatility": round(vol, 4),
        "sharpe_ratio": round(sh, 4),
        "sortino_ratio": round(sort, 4),
        "calmar_ratio": round(cal, 4),
        "max_drawdown": round(mdd, 4),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4),
        "turnover": round(turnover, 4),
        "trade_count": len(trade_logs) if trade_logs else 0
    }
