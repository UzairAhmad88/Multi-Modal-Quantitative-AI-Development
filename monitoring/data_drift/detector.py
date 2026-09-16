"""
Unified Data Drift Detector across Market, FinBERT NLP, and SEC Fundamental features.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Union
from .psi import calculate_psi
from .ks_test import calculate_ks_test
from .distance import calculate_wasserstein_distance
from ..core.monitor_result import DriftMetricResult


class DataDriftDetector:
    """Evaluates multi-feature data drift between baseline and target DataFrames or dicts."""

    def __init__(
        self,
        psi_warning_threshold: float = 0.10,
        psi_critical_threshold: float = 0.25,
        ks_pvalue_threshold: float = 0.05,
    ):
        self.psi_warning_threshold = psi_warning_threshold
        self.psi_critical_threshold = psi_critical_threshold
        self.ks_pvalue_threshold = ks_pvalue_threshold

    def evaluate_feature_drift(
        self,
        baseline_df: Union[pd.DataFrame, Dict[str, np.ndarray]],
        target_df: Union[pd.DataFrame, Dict[str, np.ndarray]],
        feature_columns: List[str] = None,
    ) -> List[DriftMetricResult]:
        results = []

        if isinstance(baseline_df, pd.DataFrame):
            if feature_columns is None:
                feature_columns = [col for col in baseline_df.columns if np.issubdtype(baseline_df[col].dtype, np.number)]
            baseline_dict = {col: baseline_df[col].values for col in feature_columns if col in baseline_df.columns}
        else:
            baseline_dict = baseline_df

        if isinstance(target_df, pd.DataFrame):
            target_dict = {col: target_df[col].values for col in feature_columns if col in target_df.columns}
        else:
            target_dict = target_df

        if feature_columns is None:
            feature_columns = list(baseline_dict.keys())

        for col in feature_columns:
            if col not in baseline_dict or col not in target_dict:
                continue

            b_vals = np.asarray(baseline_dict[col], dtype=float)
            t_vals = np.asarray(target_dict[col], dtype=float)

            psi_score = calculate_psi(b_vals, t_vals)
            ks_stat, ks_pval = calculate_ks_test(b_vals, t_vals)
            wass_dist = calculate_wasserstein_distance(b_vals, t_vals)

            is_drifted = (psi_score >= self.psi_warning_threshold) or (ks_pval < self.ks_pvalue_threshold)

            if psi_score >= self.psi_critical_threshold:
                severity = "SIGNIFICANT"
            elif psi_score >= self.psi_warning_threshold:
                severity = "MODERATE"
            else:
                severity = "NONE"

            evidence = {
                "baseline_mean": float(np.nanmean(b_vals)) if len(b_vals) > 0 else 0.0,
                "target_mean": float(np.nanmean(t_vals)) if len(t_vals) > 0 else 0.0,
                "baseline_std": float(np.nanstd(b_vals)) if len(b_vals) > 0 else 0.0,
                "target_std": float(np.nanstd(t_vals)) if len(t_vals) > 0 else 0.0,
            }

            results.append(
                DriftMetricResult(
                    feature_name=col,
                    psi_score=psi_score,
                    ks_statistic=ks_stat,
                    ks_pvalue=ks_pval,
                    wasserstein_distance=wass_dist,
                    is_drifted=is_drifted,
                    severity=severity,
                    evidence=evidence,
                )
            )

        return results
