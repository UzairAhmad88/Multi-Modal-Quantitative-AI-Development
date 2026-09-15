from __future__ import annotations
import pandas as pd

def clean_timeseries(df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
    out = df.copy()
    out[timestamp_col] = pd.to_datetime(out[timestamp_col], utc=True)
    return out.drop_duplicates().sort_values(timestamp_col).reset_index(drop=True)
