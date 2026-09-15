import numpy as np
import pandas as pd

def annualized_volatility(returns: pd.Series) -> float:
    return float(returns.std() * np.sqrt(252))
