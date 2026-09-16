"""
Prediction Output Distribution Shift Engine.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any
from ..data_drift.psi import calculate_psi
from ..data_drift.ks_test import calculate_ks_test


def calculate_prediction_distribution_shift(
    baseline_predictions: np.ndarray,
    target_predictions: np.ndarray,
) -> Dict[str, Any]:
    b_preds = np.asarray(baseline_predictions, dtype=float)
    t_preds = np.asarray(target_predictions, dtype=float)

    b_preds = b_preds[~np.isnan(b_preds)]
    t_preds = t_preds[~np.isnan(t_preds)]

    if len(b_preds) == 0 or len(t_preds) == 0:
        return {
            "psi": 0.0,
            "ks_stat": 0.0,
            "ks_pvalue": 1.0,
            "mean_shift": 0.0,
            "std_shift": 0.0,
            "is_drifted": False,
        }

    psi_val = calculate_psi(b_preds, t_preds)
    ks_stat, ks_pval = calculate_ks_test(b_preds, t_preds)

    b_mean = float(np.mean(b_preds))
    t_mean = float(np.mean(t_preds))
    b_std = float(np.std(b_preds))
    t_std = float(np.std(t_preds))

    mean_shift = t_mean - b_mean
    std_shift = t_std - b_std

    is_drifted = psi_val >= 0.10 or ks_pval < 0.05

    return {
        "psi": psi_val,
        "ks_stat": ks_stat,
        "ks_pvalue": ks_pval,
        "baseline_mean": b_mean,
        "target_mean": t_mean,
        "mean_shift": mean_shift,
        "baseline_std": b_std,
        "target_std": t_std,
        "std_shift": std_shift,
        "is_drifted": is_drifted,
    }
