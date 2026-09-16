"""
Golden Synthetic Dataset Generator for End-to-End Quant Pipeline Testing.
"""

import numpy as np
import pandas as pd
from typing import Tuple

def generate_golden_dataset(n_samples: int = 250, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generates deterministic, versioned, small golden test datasets."""
    np.random.seed(seed)
    dates = pd.date_range("2024-01-01", periods=n_samples, freq="B")

    market_df = pd.DataFrame({
        "timestamp": dates,
        "open": np.random.normal(150.0, 5.0, n_samples),
        "high": np.random.normal(153.0, 5.0, n_samples),
        "low": np.random.normal(148.0, 5.0, n_samples),
        "close": np.random.normal(151.0, 5.0, n_samples),
        "volume": np.random.randint(1000000, 5000000, n_samples),
    })

    news_df = pd.DataFrame({
        "timestamp": dates,
        "sentiment_score": np.random.normal(0.12, 0.15, n_samples),
    })

    fundamentals_df = pd.DataFrame({
        "timestamp": dates,
        "pe_ratio": np.random.normal(21.0, 1.5, n_samples),
        "pb_ratio": np.random.normal(3.2, 0.4, n_samples),
    })

    return market_df, news_df, fundamentals_df
