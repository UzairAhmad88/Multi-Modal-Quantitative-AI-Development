"""
Overfitting Diagnostics & Train/Test Generalization Gap Analysis.
"""

import numpy as np
from typing import Dict, Any, List
from validation.schemas.validation_schema import IntegrityFlag, IntegrityFlagType, IntegrityFlagSeverity


class OverfittingDiagnostics:
    """
    Evaluates evidence of potential overfitting via train/test metric degradation gaps and parameter instability.
    """

    @staticmethod
    def evaluate_generalization_gap(
        train_sharpe: float, test_sharpe: float, threshold_gap: float = 0.5
    ) -> Dict[str, Any]:
        gap = train_sharpe - test_sharpe
        degradation_pct = (gap / train_sharpe * 100.0) if train_sharpe > 0 else 0.0

        is_high_gap = gap > threshold_gap

        flags = []
        if is_high_gap:
            flags.append(
                IntegrityFlag(
                    flag_type=IntegrityFlagType.TRAIN_TEST_GAP,
                    severity=IntegrityFlagSeverity.WARNING,
                    message=f"High train/test performance gap detected (Train Sharpe: {train_sharpe:.2f}, Test Sharpe: {test_sharpe:.2f}, Gap: {gap:.2f})",
                    details={"train_sharpe": train_sharpe, "test_sharpe": test_sharpe, "gap": gap},
                )
            )

        return {
            "train_sharpe": train_sharpe,
            "test_sharpe": test_sharpe,
            "gap": round(gap, 4),
            "degradation_percent": round(degradation_pct, 2),
            "is_high_gap": is_high_gap,
            "integrity_flags": flags,
        }
