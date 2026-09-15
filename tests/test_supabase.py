import pytest
import pandas as pd
from src.db.supabase_client import SupabaseQuantClient
from src.db.sync_to_supabase import SupabaseDataSyncer

def test_supabase_client_initialization():
    client = SupabaseQuantClient()
    assert client.url is not None
    assert client.key is not None

def test_supabase_mock_insert_signals():
    client = SupabaseQuantClient()
    df = pd.DataFrame([
        {"ticker": "AAPL", "signal": "BUY", "forecast_return_5d": 0.0284, "confidence_score": 0.87},
        {"ticker": "NVDA", "signal": "STRONG BUY", "forecast_return_5d": 0.0412, "confidence_score": 0.91}
    ])
    res = client.insert_signals(df)
    assert res["status"] in ["mock", "success"]
    assert res["count"] == 2

def test_supabase_syncer():
    client = SupabaseQuantClient()
    syncer = SupabaseDataSyncer(client)
    df = pd.DataFrame([{"ticker": "MSFT", "signal": "BUY", "forecast_return_5d": 0.0215}])
    risk = {"portfolio_value": 1000000.0, "sharpe_ratio": 1.72}
    res = syncer.sync_all(df, {}, risk)
    assert res["status"] == "completed"
    assert res["ticker_count"] == 1
