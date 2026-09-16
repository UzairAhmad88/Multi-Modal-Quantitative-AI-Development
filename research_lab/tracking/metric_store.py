"""
Metric Store: Standardized logging and retrieval of experiment run metrics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class MetricStore:
    """Stores structured metrics across experiment runs."""

    def __init__(self):
        self.metrics_log: List[Dict[str, Any]] = []

    def log_metric(
        self,
        experiment_id: str,
        run_id: str,
        metric_name: str,
        value: float,
        category: str = "performance",
        split: str = "test"
    ):
        """Records a single metric entry."""
        entry = {
            "experiment_id": experiment_id,
            "run_id": run_id,
            "metric": metric_name,
            "value": round(float(value), 6),
            "category": category,
            "split": split,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self.metrics_log.append(entry)
        return entry

    def get_run_metrics(self, run_id: str) -> Dict[str, float]:
        """Retrieves dictionary of metrics for a given run."""
        return {m["metric"]: m["value"] for m in self.metrics_log if m["run_id"] == run_id}
