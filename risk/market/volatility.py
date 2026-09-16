"""
Market Volatility Analytics for Advanced Risk Engine OS.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


class VolatilityAnalyzer:
    """Computes historical, rolling, and EWMA volatility measures."""

    @staticmethod
    def calculate_historical_volatility(
        returns: np.ndarray,
        annualize: bool = True,
        scale_factor: int = 252,
    ) -> float:
        """Calculate sample annual volatility."""
        r = np.array(returns, dtype=float)
        if len(r) < 2:
            return 0.0
        vol = float(np.std(r, ddof=1))
        if annualize:
            vol = vol * np.sqrt(scale_factor)
        return float(vol)

    @staticmethod
    def calculate_rolling_volatility(
        returns: np.ndarray,
        window: int = 20,
        scale_factor: int = 252,
    ) -> np.ndarray:
        """Compute rolling annualized volatility series."""
        s = pd.Series(returns)
        roll_vol = s.rolling(window=window).std(ddof=1) * np.sqrt(scale_factor)
        return roll_vol.fillna(0.0).values

    @staticmethod
    def calculate_ewma_volatility(
        returns: np.ndarray,
        halflife: int = 60,
        scale_factor: int = 252,
    ) -> float:
        """Compute Exponentially Weighted Moving Average (EWMA) annualized volatility."""
        s = pd.Series(returns)
        ewma_var = s.ewm(halflife=halflife).var().values[-1]
        ewma_vol = np.sqrt(max(0.0, float(ewma_var))) * np.sqrt(scale_factor)
        return float(ewma_vol)
