import pandas as pd
from src.data.market_loader import load_market_data, MarketDataCleaner, MarketDataValidator, generate_demo_market_data

def test_generate_demo_market_data():
    df = generate_demo_market_data("AAPL", "2023-01-01", "2023-12-31")
    assert not df.empty
    assert len(df) > 200
    assert set(["date", "ticker", "open", "high", "low", "close", "volume"]).issubset(df.columns)
    assert (df["high"] >= df["low"]).all()

def test_market_cleaner():
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-01", "2023-01-02"],
        "Open": [100, 100, 101],
        "High": [105, 105, 106],
        "Low": [99, 99, 100],
        "Close": [102, 102, 104],
        "Volume": [1000, 1000, 1500]
    })
    cleaned = MarketDataCleaner.clean(df, "AAPL")
    assert len(cleaned) == 2  # duplicate removed
    assert "date" in cleaned.columns
    assert "ticker" in cleaned.columns

def test_load_market_data():
    df = load_market_data("AAPL", start="2023-01-01", end="2023-06-01")
    assert not df.empty
    assert MarketDataValidator.validate_schema(df)


def test_stochastic_oscillator():
    from src.features.technical import compute_stochastic_oscillator, add_technical_features
    df = generate_demo_market_data("MSFT", "2023-01-01", "2023-06-01")
    k, d = compute_stochastic_oscillator(df["high"], df["low"], df["close"])
    assert len(k) == len(df)
    assert len(d) == len(df)
    assert (k >= 0).all() and (k <= 100).all()
    assert (d >= 0).all() and (d <= 100).all()

    df_feat = add_technical_features(df)
    assert "stoch_k_14" in df_feat.columns
    assert "stoch_d_3" in df_feat.columns


def test_market_import_endpoint():
    from fastapi.testclient import TestClient
    from api.main import app
    client = TestClient(app)
    res = client.post("/api/data/market/import", json={"ticker": "MSFT", "start_date": "2024-01-01", "force_live_api": False})
    assert res.status_code == 200
    data = res.json()
    assert data["ticker"] == "MSFT"
    assert "stochastic" in data
    assert "stoch_k" in data["stochastic"]
    assert "stoch_d" in data["stochastic"]

    res_stoch = client.get("/api/data/market/stoch/MSFT")
    assert res_stoch.status_code == 200
    stoch_data = res_stoch.json()
    assert stoch_data["ticker"] == "MSFT"
    assert "current_stoch_k" in stoch_data

