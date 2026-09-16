"""
Overfitting Detector for Quantitative AI Models.
Calculates generalization gaps, performance decay across slices, and detects parameter sensitivity instability.
"""

from typing import Dict, List, Any, Optional


class OverfittingDetector:
    """Diagnoses overfitting using performance decay across train, validation, test, and paper windows."""

    @staticmethod
    def evaluate_generalization_gap(
        train_metric: float,
        val_metric: float,
        test_metric: float,
        paper_metric: Optional[float] = None,
        max_acceptable_gap: float = 0.35,
    ) -> Dict[str, Any]:
        """Calculates generalization gap = val_metric - test_metric and train_metric - test_metric."""
        val_test_gap = round(val_metric - test_metric, 4)
        train_test_gap = round(train_metric - test_metric, 4)

        is_overfitted = train_test_gap > max_acceptable_gap
        decay = {
            "train": train_metric,
            "validation": val_metric,
            "test": test_metric,
        }
        if paper_metric is not None:
            decay["paper_trading"] = paper_metric

        return {
            "status": "WARNING" if is_overfitted else "PASSED",
            "is_overfitted": is_overfitted,
            "generalization_gap_val_test": val_test_gap,
            "generalization_gap_train_test": train_test_gap,
            "performance_decay": decay,
            "conclusion": (
                f"Elevated generalization gap ({train_test_gap:.2f}) indicates potential overfitting."
                if is_overfitted
                else "Generalization gap is within acceptable research limits."
            ),
        }
