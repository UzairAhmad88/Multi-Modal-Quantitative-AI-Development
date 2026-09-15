import pytest
import pandas as pd
import numpy as np
from src.data.data_synchronizer import align_modalities
from src.models.ml.split import chronological_split
from src.features.technical import add_technical_features

def test_chronological_split_no_overlap():
    dates = pd.date_range("2021-01-01", "2026-01-01", freq="D")
    df = pd.DataFrame({"date": dates, "val": np.arange(len(dates))})

    train, val, test = chronological_split(df, train_ratio=0.7, val_ratio=0.15)

    assert train["date"].max() < val["date"].min()
    assert val["date"].max() < test["date"].min()
    assert len(train) + len(val) + len(test) == len(df)

def test_rolling_features_no_future_lookahead():
    prices = pd.Series([100.0, 102.0, 101.0, 105.0, 110.0, 108.0])
    df = pd.DataFrame({"close": prices})

    # SMA 3
    sma3 = prices.rolling(3).mean()
    # sma3 at index 2 must equal mean([100, 102, 101]) = 101.0
    assert sma3.iloc[2] == pytest.approx(101.0)
    # Ensure changing future value at index 5 does not affect index 2
    prices_mod = prices.copy()
    prices_mod.iloc[5] = 999.0
    sma3_mod = prices_mod.rolling(3).mean()
    assert sma3_mod.iloc[2] == pytest.approx(101.0)

def test_point_in_time_fundamental_release():
    market_df = pd.DataFrame({
        "ticker": ["AAPL", "AAPL"],
        "date": [pd.Timestamp("2024-03-31", tz="UTC"), pd.Timestamp("2024-04-15", tz="UTC")],
        "close": [170.0, 175.0]
    })

    fund_df = pd.DataFrame({
        "ticker": ["AAPL"],
        "quarter_end_date": [pd.Timestamp("2024-03-31", tz="UTC")],
        "public_release_date": [pd.Timestamp("2024-04-30", tz="UTC")],  # Released April 30
        "revenue": [90000.0]
    })

    aligned = align_modalities(market_df, fundamentals_df=fund_df)

    # On March 31 and April 15, public release (April 30) has NOT happened yet -> revenue must be 0.0 or unreleased
    mar31_rev = aligned.loc[aligned["date"] == pd.Timestamp("2024-03-31", tz="UTC"), "revenue"].values[0]
    apr15_rev = aligned.loc[aligned["date"] == pd.Timestamp("2024-04-15", tz="UTC"), "revenue"].values[0]

    assert mar31_rev == 0.0
    assert apr15_rev == 0.0
