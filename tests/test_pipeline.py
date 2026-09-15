import pytest
from scripts.run_pipeline import run_pipeline

def test_full_pipeline_demo_execution():
    res = run_pipeline(demo=True, ticker="AAPL", start_date="2020-01-01")
    assert res is not None
    assert "backtest_cagr" in res
    assert "backtest_sharpe" in res
    assert res["risk_status"] == "NORMAL"
