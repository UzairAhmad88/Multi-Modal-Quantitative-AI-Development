import pandas as pd

def drawdown(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1

def max_drawdown(equity: pd.Series) -> float:
    return float(drawdown(equity).min())
