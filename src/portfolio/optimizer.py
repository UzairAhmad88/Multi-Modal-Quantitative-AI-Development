import pandas as pd

def minimum_variance_weights(returns: pd.DataFrame):
    return pd.Series(1.0 / returns.shape[1], index=returns.columns)
