import pandas as pd

def historical_var(returns: pd.Series, confidence=0.95) -> float:
    return float(-returns.quantile(1 - confidence))
