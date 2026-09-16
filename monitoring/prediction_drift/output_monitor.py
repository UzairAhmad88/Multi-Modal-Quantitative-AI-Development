"""
Output Prediction & Confidence Decay Monitor.
"""

import numpy as np
from typing import Dict, Any, Optional
from .distribution_shift import calculate_prediction_distribution_shift


class OutputPredictionMonitor:
    """Monitors output predictions and alpha signal confidence drift."""

    def __init__(self, psi_threshold: float = 0.15):
        self.psi_threshold = psi_threshold

    def monitor(
        self,
        baseline_preds: np.ndarray,
        target_preds: np.ndarray,
        baseline_confs: Optional[np.ndarray] = None,
        target_confs: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        pred_shift = calculate_prediction_distribution_shift(baseline_preds, target_preds)

        conf_summary = {}
        if baseline_confs is not None and target_confs is not None:
            conf_b = np.asarray(baseline_confs, dtype=float)
            conf_t = np.asarray(target_confs, dtype=float)
            mean_b_conf = float(np.nanmean(conf_b)) if len(conf_b) > 0 else 0.0
            mean_t_conf = float(np.nanmean(conf_t)) if len(conf_t) > 0 else 0.0
            conf_decay_pct = (mean_b_conf - mean_t_conf) / max(abs(mean_b_conf), 1e-6)

            conf_summary = {
                "baseline_mean_confidence": mean_b_conf,
                "target_mean_confidence": mean_t_conf,
                "confidence_decay_pct": conf_decay_pct,
                "is_confidence_decayed": conf_decay_pct > 0.20,
            }

        return {
            "prediction_shift": pred_shift,
            "confidence_summary": conf_summary,
            "is_output_drifted": pred_shift["is_drifted"],
        }
