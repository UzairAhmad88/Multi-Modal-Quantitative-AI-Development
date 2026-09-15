import pandas as pd

def gross_exposure(weights: pd.Series) -> float:
    return float(weights.abs().sum())
