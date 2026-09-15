from __future__ import annotations
import numpy as np
import pandas as pd


def compute_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index (RSI)."""
    delta = close.diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=window).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.fillna(50.0)


def compute_macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Moving Average Convergence Divergence (MACD)."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    macd_hist = macd_line - signal_line
    return macd_line, signal_line, macd_hist


def compute_bollinger_bands(
    close: pd.Series, window: int = 20, num_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands (Upper, Lower, Bandwidth, %B)."""
    sma = close.rolling(window=window).mean()
    std = close.rolling(window=window).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    bandwidth = (upper - lower) / (sma + 1e-10)
    pct_b = (close - lower) / ((upper - lower) + 1e-10)
    return upper, lower, bandwidth, pct_b


def compute_atr(
    high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14
) -> pd.Series:
    """Average True Range (ATR)."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    return atr.bfill().fillna(0.0)


def add_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute comprehensive technical analysis features for OHLCV dataframe."""
    out = df.copy()
    close = out["close"]
    high = out.get("high", close)
    low = out.get("low", close)
    volume = out.get("volume", pd.Series(1, index=out.index))

    # Returns
    out["return_1d"] = close.pct_change(1)
    out["return_5d"] = close.pct_change(5)
    out["return_10d"] = close.pct_change(10)
    out["return_20d"] = close.pct_change(20)

    # Log Returns
    out["log_return_1d"] = np.log(close / close.shift(1))
    out["log_return_5d"] = np.log(close / close.shift(5))

    # Moving Averages
    for w in [10, 20, 50, 200]:
        out[f"sma_{w}"] = close.rolling(w).mean()
        out[f"price_to_sma_{w}"] = close / (out[f"sma_{w}"] + 1e-10) - 1.0

    out["ema_12"] = close.ewm(span=12, adjust=False).mean()
    out["ema_26"] = close.ewm(span=26, adjust=False).mean()

    # RSI
    out["rsi_14"] = compute_rsi(close, 14)

    # MACD
    out["macd"], out["macd_signal"], out["macd_hist"] = compute_macd(close)

    # Bollinger Bands
    out["bollinger_upper"], out["bollinger_lower"], out["bollinger_bw"], out["bollinger_pct_b"] = (
        compute_bollinger_bands(close, 20)
    )

    # ATR
    out["atr_14"] = compute_atr(high, low, close, 14)

    # Momentum & ROC
    out["momentum_10d"] = close - close.shift(10)
    out["roc_10d"] = ((close - close.shift(10)) / (close.shift(10) + 1e-10)) * 100.0

    # Volume Features
    out["volume_change_1d"] = volume.pct_change(1)
    out["volume_sma_20"] = volume.rolling(20).mean()

    # Volatility
    for w in [10, 20, 60]:
        out[f"volatility_{w}d"] = out["return_1d"].rolling(w).std() * np.sqrt(252)

    return out


# Alias for backward compatibility
def add_basic_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    return add_technical_features(df)
