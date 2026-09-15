import pandas as pd
import numpy as np
from src.data.market_loader import generate_demo_market_data
from src.data.news_loader import generate_demo_news
from src.data.fundamental_loader import generate_demo_fundamentals
from src.backtesting.execution import execute_order
from src.backtesting.engine import BacktestEngine
from src.backtesting.metrics import compute_performance_metrics
from src.backtesting.walk_forward import WalkForwardEvaluator
from src.backtesting.ablation import AblationStudyEngine

def test_execute_order():
    new_shares, fill = execute_order(
        ticker="AAPL", date="2023-01-02", target_weight=0.20,
        current_shares=0.0, open_price=100.0, portfolio_value=100000.0,
        transaction_cost_bps=10.0, slippage_bps=5.0
    )
    assert new_shares > 0
    assert fill.fill_price > 100.0  # Slippage applied
    assert fill.transaction_fee > 0.0

def test_backtest_engine():
    market = generate_demo_market_data("AAPL", "2023-01-01", "2023-06-01")
    target_weights = pd.DataFrame(
        {"AAPL": [0.20] * len(market)},
        index=pd.to_datetime(market["date"], utc=True)
    )
    engine = BacktestEngine()
    res = engine.run(market, target_weights)

    assert "equity_curve" in res
    assert "metrics" in res
    assert res["metrics"]["sharpe_ratio"] is not None

def test_walk_forward_evaluator():
    dates = list(pd.date_range("2018-01-01", periods=1000, freq="B", tz="UTC"))
    wf = WalkForwardEvaluator(train_window_days=500, test_window_days=100)
    windows = wf.generate_windows(dates)
    assert len(windows) > 0
    assert windows[0]["train_end"] < windows[0]["test_start"]

def test_ablation_study_engine():
    market = generate_demo_market_data("AAPL", "2023-01-01", "2023-06-01")
    news = generate_demo_news(["AAPL"], "2023-01-01", "2023-06-01")
    fund = generate_demo_fundamentals(["AAPL"], 2022, 2023)

    ablation = AblationStudyEngine()
    results = ablation.run_ablation(market, news, fund)

    assert len(results) == 4
    assert "Experiment D (Market + News + Fundamentals)" in results
