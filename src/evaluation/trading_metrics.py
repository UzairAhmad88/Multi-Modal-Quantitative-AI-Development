def summarize_backtest(equity, returns):
    from src.backtesting.metrics import total_return, sharpe_ratio
    from src.risk.drawdown import max_drawdown
    return {
        "total_return": total_return(equity),
        "sharpe": sharpe_ratio(returns),
        "max_drawdown": max_drawdown(equity),
    }
