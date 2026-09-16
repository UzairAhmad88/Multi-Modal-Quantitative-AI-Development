"""
Overfitting Detector: Evaluates train-test performance gap, parameter instability, and complexity penalties.
"""

import numpy as np
from typing import Dict, Any, List


class OverfittingDetector:
    """Diagnoses strategy overfitting risks based on train/validation/test degradation."""

    def evaluate_overfitting(
        self,
        train_sharpe: float,
        test_sharpe: float,
        num_parameters: int = 5,
        num_trials: int = 10
    ) -> Dict[str, Any]:
        """Calculates degradation gap, Deflated Sharpe ratio, and overfitting risk level."""
        sharpe_gap = max(0.0, train_sharpe - test_sharpe)
        degradation_pct = (sharpe_gap / train_sharpe) if train_sharpe > 0 else 0.0

        # Heuristic deflated metric
        trial_penalty = 0.05 * np.log(max(1, num_trials))
        complexity_penalty = 0.02 * num_parameters
        deflated_sharpe = max(-1.0, test_sharpe - trial_penalty - complexity_penalty)

        if degradation_pct > 0.50 or deflated_sharpe < 0.5:
            risk_level = "HIGH_OVERFITTING_RISK"
        elif degradation_pct > 0.25:
            risk_level = "MODERATE_OVERFITTING_RISK"
        else:
            risk_level = "LOW_OVERFITTING_RISK"

        return {
            "train_sharpe": round(train_sharpe, 4),
            "test_sharpe": round(test_sharpe, 4),
            "sharpe_degradation_gap": round(sharpe_gap, 4),
            "degradation_percentage": round(degradation_pct, 4),
            "deflated_sharpe": round(float(deflated_sharpe), 4),
            "overfitting_risk_level": risk_level,
            "num_parameters": num_parameters,
            "num_trials": num_trials
        }
