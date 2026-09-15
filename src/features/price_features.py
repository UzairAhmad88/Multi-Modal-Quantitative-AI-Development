from __future__ import annotations
import numpy as np
import pandas as pd


def forward_return(df: pd.DataFrame, horizon: int = 5) -> pd.Series:
    """Compute n-day forward return: close[t+n] / close[t] - 1."""
    return df["close"].shift(-horizon) / df["close"] - 1.0


def add_target_features(
    df: pd.DataFrame,
    horizon_days: int = 5,
    buy_threshold: float = 0.015,
    sell_threshold: float = -0.015
) -> pd.DataFrame:
    """Compute continuous target returns and discrete classification labels (BUY/HOLD/SELL).

    BUY: 1, HOLD: 0, SELL: -1
    """
    out = df.copy()
    out.sort_values(["ticker", "date"], inplace=True)

    # Calculate forward returns per ticker to prevent cross-ticker target leakage
    out[f"target_return_{horizon_days}d"] = out.groupby("ticker")["close"].transform(
        lambda s: s.shift(-horizon_days) / s - 1.0
    )

    # Continuous primary target
    out["target_return"] = out[f"target_return_{horizon_days}d"]

    # Discrete classification target
    conditions = [
        out["target_return"] >= buy_threshold,
        out["target_return"] <= sell_threshold
    ]
    choices = [1, -1]  # 1: BUY, -1: SELL, 0: HOLD
    out["target_class"] = np.select(conditions, choices, default=0)

    return out
