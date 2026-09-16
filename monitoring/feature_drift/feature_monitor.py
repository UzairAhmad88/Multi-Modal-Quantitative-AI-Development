"""
Unified Feature Drift Monitor.
"""

import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
from .importance_shift import calculate_importance_shift
from .correlation_shift import calculate_correlation_matrix_shift


class FeatureDriftMonitor:
    """Monitors structural feature changes across multimodal datasets."""

    def __init__(self, max_correlation_shift_threshold: float = 0.50):
        self.max_correlation_shift_threshold = max_correlation_shift_threshold

    def audit_feature_shifts(
        self,
        baseline_df: pd.DataFrame,
        target_df: pd.DataFrame,
        baseline_importance: Optional[Dict[str, float]] = None,
        target_importance: Optional[Dict[str, float]] = None,
        feature_columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        frobenius_norm, max_shift, mean_shift = calculate_correlation_matrix_shift(
            baseline_df, target_df, features=feature_columns
        )

        importance_summary = {}
        if baseline_importance and target_importance:
            cosine_sim, rank_corr, top_k_overlap = calculate_importance_shift(
                baseline_importance, target_importance
            )
            importance_summary = {
                "cosine_similarity": cosine_sim,
                "rank_correlation": rank_corr,
                "top_k_overlap": top_k_overlap,
                "is_importance_shifted": cosine_sim < 0.85 or rank_corr < 0.70,
            }

        return {
            "frobenius_norm": frobenius_norm,
            "max_correlation_shift": max_shift,
            "mean_correlation_shift": mean_shift,
            "is_correlation_shifted": max_shift >= self.max_correlation_shift_threshold,
            "importance_summary": importance_summary,
        }
