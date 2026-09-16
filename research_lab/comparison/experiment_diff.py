"""
Experiment Diff Engine: Highlights exact configuration differences between two experiments.
"""

from typing import Dict, Any


class ExperimentDiff:
    """Computes configuration diffs between two experiments."""

    def diff_experiments(self, exp_a: Dict[str, Any], exp_b: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates key-by-key config differences."""
        diffs = {}
        keys = ["dataset_id", "feature_version", "model_version", "strategy_id", "random_seed"]

        for k in keys:
            v_a = exp_a.get(k)
            v_b = exp_b.get(k)
            if v_a != v_b:
                diffs[k] = {"exp_a": v_a, "exp_b": v_b}

        return {
            "exp_a_id": exp_a.get("experiment_id", "A"),
            "exp_b_id": exp_b.get("experiment_id", "B"),
            "configuration_diffs": diffs,
            "has_differences": len(diffs) > 0
        }
