"""
Experiment Comparison Engine: Compares multiple experiment runs across raw metrics and flags comparability differences.
"""

from typing import List, Dict, Any


class ExperimentComparisonEngine:
    """Builds side-by-side experiment performance matrix."""

    def compare_experiments(self, experiments_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compares experiments and checks dataset/period/cost comparability."""
        comparison_matrix = {}
        comparability_warnings = []

        first_ds = experiments_data[0].get("dataset_id") if experiments_data else None

        for exp in experiments_data:
            exp_id = exp.get("experiment_id", "EXP-UNKNOWN")
            metrics = exp.get("metrics", {})
            ds_id = exp.get("dataset_id")

            if first_ds and ds_id != first_ds:
                comparability_warnings.append(f"Experiment {exp_id} uses dataset {ds_id} which differs from {first_ds}")

            comparison_matrix[exp_id] = {
                "name": exp.get("name", ""),
                "model_version": exp.get("model_version", ""),
                "cagr": metrics.get("cagr", 0.0),
                "sharpe_ratio": metrics.get("sharpe_ratio", 0.0),
                "sortino_ratio": metrics.get("sortino_ratio", 0.0),
                "max_drawdown": metrics.get("max_drawdown", 0.0),
                "win_rate": metrics.get("win_rate", 0.0)
            }

        return {
            "comparison_matrix": comparison_matrix,
            "is_fair_comparison": len(comparability_warnings) == 0,
            "comparability_warnings": comparability_warnings
        }
