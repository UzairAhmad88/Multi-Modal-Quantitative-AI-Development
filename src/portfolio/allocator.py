from __future__ import annotations
import pandas as pd
import numpy as np
from src.portfolio.position_sizing import cap_weights


def equal_weight(tickers: list[str]) -> pd.Series:
    """Equal weight allocation across universe."""
    if not tickers:
        return pd.Series(dtype=float)
    w = 1.0 / len(tickers)
    return pd.Series(w, index=tickers)


def alpha_weighted(alphas: pd.Series, max_position: float = 0.25) -> pd.Series:
    """Proportional weight allocation based on positive alpha scores."""
    longs = alphas.clip(lower=0.0)
    total = longs.sum()
    if total > 1e-8:
        raw_weights = longs / total
    else:
        raw_weights = equal_weight(list(alphas.index))
    return cap_weights(raw_weights, maximum=max_position)


def volatility_adjusted(alphas: pd.Series, volatilities: pd.Series, max_position: float = 0.25) -> pd.Series:
    """Volatility-adjusted alpha weighting (higher alpha / lower volatility gets higher weight)."""
    raw = alphas.clip(lower=0.0) / (volatilities + 1e-4)
    total = raw.sum()
    if total > 1e-8:
        weights = raw / total
    else:
        weights = equal_weight(list(alphas.index))
    return cap_weights(weights, maximum=max_position)


def risk_parity(returns_df: pd.DataFrame, max_position: float = 0.25) -> pd.Series:
    """Risk parity allocation weighting inversely to asset volatility."""
    vols = returns_df.std() * np.sqrt(252)
    inv_vols = 1.0 / (vols + 1e-4)
    weights = inv_vols / inv_vols.sum()
    return cap_weights(weights, maximum=max_position)
