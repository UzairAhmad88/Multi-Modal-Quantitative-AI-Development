"""
Correlation Matrix Shift Auditor.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


def calculate_correlation_matrix_shift(
    baseline_df: pd.DataFrame,
    target_df: pd.DataFrame,
    features: List[str] = None,
) -> Tuple[float, float, float]:
    """Calculates Frobenius norm shift, max elementwise shift, and mean correlation shift between baseline and target correlation matrices."""
    if features is None:
        features = [col for col in baseline_df.columns if np.issubdtype(baseline_df[col].dtype, np.number)]

    common_features = [f for f in features if f in baseline_df.columns and f in target_df.columns]
    if len(common_features) < 2:
        return 0.0, 0.0, 0.0

    corr_b = baseline_df[common_features].corr().fillna(0.0).values
    corr_t = target_df[common_features].corr().fillna(0.0).values

    diff_matrix = corr_t - corr_b
    frobenius_norm = float(np.linalg.norm(diff_matrix, ord="fro"))
    max_shift = float(np.max(np.abs(diff_matrix)))
    mean_shift = float(np.mean(np.abs(diff_matrix)))

    return frobenius_norm, max_shift, mean_shift
