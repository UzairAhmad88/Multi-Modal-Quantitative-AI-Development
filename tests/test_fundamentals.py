import pandas as pd
from src.data.fundamental_loader import (
    load_fundamentals, generate_demo_fundamentals, FundamentalCleaner, FundamentalValidator, REQUIRED_FUNDAMENTAL_COLUMNS
)
from src.features.fundamental_features import build_fundamental_features

def test_generate_demo_fundamentals():
    df = generate_demo_fundamentals(["AAPL", "MSFT"])
    assert not df.empty
    assert set(REQUIRED_FUNDAMENTAL_COLUMNS).issubset(df.columns)
    assert (df["public_release_date"] >= df["quarter_end_date"]).all()

def test_build_fundamental_features():
    df = generate_demo_fundamentals(["AAPL"])
    feats = build_fundamental_features(df)
    assert "net_margin" in feats.columns
    assert "roe" in feats.columns
    assert "debt_to_equity" in feats.columns
    assert "revenue_growth_yoy" in feats.columns

def test_load_fundamentals():
    df = load_fundamentals("AAPL")
    assert not df.empty
