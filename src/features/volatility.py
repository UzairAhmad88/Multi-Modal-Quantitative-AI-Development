from __future__ import annotations
import numpy as np
import pandas as pd

def annualized_volatility(returns: pd.Series, periods: int = 252) -> pd.Series:
    return returns.rolling(20).std() * np.sqrt(periods)
