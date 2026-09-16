"""
OOS Prediction Error & Accuracy Decay Tracker.
"""

import numpy as np
from typing import Dict, Any


def calculate_accuracy_decay(
    baseline_actuals: np.ndarray,
    baseline_predictions: np.ndarray,
    target_actuals: np.ndarray,
    target_predictions: np.ndarray,
) -> Dict[str, Any]:
    """Calculates error degradation (MAE, RMSE, directional accuracy) between baseline and target windows."""
    b_act = np.asarray(baseline_actuals, dtype=float)
    b_pred = np.asarray(baseline_predictions, dtype=float)
    t_act = np.asarray(target_actuals, dtype=float)
    t_pred = np.asarray(target_predictions, dtype=float)

    b_mae = float(np.mean(np.abs(b_act - b_pred))) if len(b_act) > 0 else 0.0
    t_mae = float(np.mean(np.abs(t_act - t_pred))) if len(t_act) > 0 else 0.0

    b_rmse = float(np.sqrt(np.mean((b_act - b_pred) ** 2))) if len(b_act) > 0 else 0.0
    t_rmse = float(np.sqrt(np.mean((t_act - t_pred) ** 2))) if len(t_act) > 0 else 0.0

    b_dir = float(np.mean(np.sign(b_act) == np.sign(b_pred))) if len(b_act) > 0 else 0.5
    t_dir = float(np.mean(np.sign(t_act) == np.sign(t_pred))) if len(t_act) > 0 else 0.5

    mae_increase_pct = (t_mae - b_mae) / max(b_mae, 1e-6)
    dir_decay_pct = (b_dir - t_dir) / max(b_dir, 1e-6)

    return {
        "baseline_mae": b_mae,
        "target_mae": t_mae,
        "mae_increase_pct": mae_increase_pct,
        "baseline_rmse": b_rmse,
        "target_rmse": t_rmse,
        "baseline_directional_acc": b_dir,
        "target_directional_acc": t_dir,
        "directional_acc_decay_pct": dir_decay_pct,
        "is_accuracy_decayed": mae_increase_pct > 0.25 or dir_decay_pct > 0.15,
    }
