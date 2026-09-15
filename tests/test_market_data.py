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
