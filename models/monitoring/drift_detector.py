"""
Model Drift Detector for Prediction and Feature Distribution Monitoring.
Detects statistical drift using Kolmogorov-Smirnov two-sample tests.
"""

from typing import Dict, Any, List
import numpy as np
from scipy import stats


class ModelDriftDetector:
    """Monitors feature and prediction distribution drift."""

    def detect_drift(
        self,
        reference_data: np.ndarray,
        current_data: np.ndarray,
        p_threshold: float = 0.05
    ) -> Dict[str, Any]:
        """Performs two-sample Kolmogorov-Smirnov test to detect distribution drift."""
        ref = np.array(reference_data).flatten()
        curr = np.array(current_data).flatten()

        if len(ref) < 10 or len(curr) < 10:
            return {"status": "INSUFFICIENT_DATA", "drift_detected": False}

        ks_stat, p_val = stats.ks_2samp(ref, curr)
        drift_detected = bool(p_val < p_threshold)

        return {
            "status": "SUCCESS",
            "ks_statistic": round(float(ks_stat), 4),
            "p_value": round(float(p_val), 6),
            "drift_detected": drift_detected,
            "summary": "STATISTICAL DRIFT DETECTED" if drift_detected else "NO DRIFT DETECTED"
        }
