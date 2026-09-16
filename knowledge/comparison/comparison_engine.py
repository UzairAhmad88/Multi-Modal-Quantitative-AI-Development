"""
Experiment Comparison Engine & Delta Analyzer.
"""

from typing import Dict, Any, List, Optional
from knowledge.schemas.knowledge_record import ResearchKnowledgeRecord
from knowledge.repository.knowledge_repository import KnowledgeRepository


class ExperimentComparisonEngine:
    """
    Compares research experiments side-by-side, calculates metric deltas, and validates comparability.
    """

    def __init__(self, repo: KnowledgeRepository = None):
        self.repo = repo or KnowledgeRepository()

    def compare_experiments(self, exp_id_a: str, exp_id_b: str) -> Dict[str, Any]:
        rec_a = self.repo.get_record(exp_id_a)
        rec_b = self.repo.get_record(exp_id_b)

        if not rec_a:
            raise ValueError(f"Experiment '{exp_id_a}' not found in knowledge repository")
        if not rec_b:
            raise ValueError(f"Experiment '{exp_id_b}' not found in knowledge repository")

        # Check comparability warnings
        warnings = []
        if rec_a.dataset_id != rec_b.dataset_id:
            warnings.append(f"Different Datasets: '{rec_a.dataset_id}' vs '{rec_b.dataset_id}'")
        if set(rec_a.modalities) != set(rec_b.modalities):
            warnings.append(f"Different Modalities: {rec_a.modalities} vs {rec_b.modalities}")

        # Metrics comparison
        all_metric_keys = set(rec_a.metrics.keys()).union(set(rec_b.metrics.keys()))
        metrics_table = []

        for key in sorted(all_metric_keys):
            val_a = rec_a.metrics.get(key, None)
            val_b = rec_b.metrics.get(key, None)

            delta = None
            pct_change = None

            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                delta = round(val_b - val_a, 4)
                if val_a != 0:
                    pct_change = round((delta / abs(val_a)) * 100.0, 2)

            metrics_table.append({
                "metric": key,
                "experiment_a": val_a,
                "experiment_b": val_b,
                "delta": delta,
                "percent_change": pct_change,
            })

        # Configuration diff
        config_diff = {
            "dataset_id": {"a": rec_a.dataset_id, "b": rec_b.dataset_id},
            "feature_set_id": {"a": rec_a.feature_set_id, "b": rec_b.feature_set_id},
            "model_id": {"a": rec_a.model_id, "b": rec_b.model_id},
            "strategy_id": {"a": rec_a.strategy_id, "b": rec_b.strategy_id},
            "modalities": {"a": rec_a.modalities, "b": rec_b.modalities},
        }

        return {
            "experiment_a": rec_a.experiment_id,
            "experiment_b": rec_b.experiment_id,
            "is_fair_comparison": len(warnings) == 0,
            "warnings": warnings,
            "metrics_comparison": metrics_table,
            "configuration_diff": config_diff,
        }
