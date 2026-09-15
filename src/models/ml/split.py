from __future__ import annotations
from typing import Tuple
import pandas as pd
import numpy as np


def chronological_split(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    date_col: str = "date"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split dataframe into Train, Validation, and Test sets strictly chronologically.

    No random shuffling is performed to prevent lookahead data leakage.
    """
    out = df.sort_values(date_col).reset_index(drop=True)
    n = len(out)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_df = out.iloc[:train_end].reset_index(drop=True)
    val_df = out.iloc[train_end:val_end].reset_index(drop=True)
    test_df = out.iloc[val_end:].reset_index(drop=True)

    return train_df, val_df, test_df
