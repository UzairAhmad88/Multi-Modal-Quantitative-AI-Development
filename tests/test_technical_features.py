import pandas as pd
import numpy as np
from src.features.technical import (
    add_technical_features, compute_rsi, compute_macd, compute_bollinger_bands, compute_atr
)

def test_rsi_range():
    close = pd.Series([10, 11, 12, 11, 10, 12, 13, 14, 15, 14, 13, 12, 13, 14, 15])
    rsi = compute_rsi(close, window=5)
    assert (rsi >= 0).all() and (rsi <= 100).all()

def test_macd():
    close = pd.Series(np.linspace(10, 50, 100))
    macd, signal, hist = compute_macd(close)
    assert len(macd) == 100
    assert len(signal) == 100
    assert len(hist) == 100

def test_bollinger_bands():
    close = pd.Series(np.random.default_rng(42).normal(100, 5, 50))
    upper, lower, bw, pct_b = compute_bollinger_bands(close, window=10)
    valid_idx = 10
    assert (upper.iloc[valid_idx:] >= lower.iloc[valid_idx:]).all()

def test_technical_features_dataframe():
    df = pd.DataFrame({
        "open": range(1, 101),
        "high": range(2, 102),
        "low": range(1, 101),
        "close": range(1, 101),
        "volume": [1000] * 100
    })
    out = add_technical_features(df)
    expected_cols = [
        "return_1d", "rsi_14", "macd", "bollinger_upper",
        "atr_14", "momentum_10d", "volatility_20d"
    ]
    for c in expected_cols:
        assert c in out.columns
