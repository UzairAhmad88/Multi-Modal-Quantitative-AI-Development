"""
Experiment Comparator Engine for Research Intelligence.
Performs multi-metric differential comparison across experiments without boiling down to a single score.
"""

from typing import Dict, List, Any, Optional
from research_intelligence.experiment_manager.manager import ExperimentRecord


class ExperimentComparator:
    """Compares metrics and configurations across experiments side-by-side."""

    @staticmethod
    def compare(exp1: ExperimentRecord, exp2: ExperimentRecord) -> Dict[str, Any]:
        """Compares two experiments across dataset, features, model, and performance metrics."""
        cfg1, res1 = exp1.config, exp1.results or {}
        cfg2, res2 = exp2.config, exp2.results or {}

        t1 = res1.get("trading_metrics", {})
        t2 = res2.get("trading_metrics", {})
        p1 = res1.get("prediction_metrics", {})
        p2 = res2.get("prediction_metrics", {})
        c1 = res1.get("cost_metrics", {})
        c2 = res2.get("cost_metrics", {})

        # Differential features
        added_features = list(set(cfg2.features) - set(cfg1.features))
        removed_features = list(set(cfg1.features) - set(cfg2.features))

        comparison = {
            "experiment_a": {
                "id": exp1.experiment_id,
                "name": cfg1.name,
                "dataset": cfg1.dataset,
                "model": cfg1.model,
                "features": cfg1.features,
            },
            "experiment_b": {
                "id": exp2.experiment_id,
                "name": cfg2.name,
                "dataset": cfg2.dataset,
                "model": cfg2.model,
                "features": cfg2.features,
            },
            "configuration_diff": {
                "added_features": added_features,
                "removed_features": removed_features,
                "model_changed": cfg1.model != cfg2.model,
                "dataset_changed": cfg1.dataset != cfg2.dataset,
            },
            "metrics_comparison": {
                "directional_accuracy": {
                    "exp_a": p1.get("directional_accuracy"),
                    "exp_b": p2.get("directional_accuracy"),
                    "diff": (p2.get("directional_accuracy", 0) or 0) - (p1.get("directional_accuracy", 0) or 0),
                },
                "cagr": {
                    "exp_a": t1.get("cagr"),
                    "exp_b": t2.get("cagr"),
                    "diff": (t2.get("cagr", 0) or 0) - (t1.get("cagr", 0) or 0),
                },
                "sharpe": {
                    "exp_a": t1.get("sharpe"),
                    "exp_b": t2.get("sharpe"),
                    "diff": (t2.get("sharpe", 0) or 0) - (t1.get("sharpe", 0) or 0),
                },
                "sortino": {
                    "exp_a": t1.get("sortino"),
                    "exp_b": t2.get("sortino"),
                    "diff": (t2.get("sortino", 0) or 0) - (t1.get("sortino", 0) or 0),
                },
                "max_drawdown": {
                    "exp_a": t1.get("max_drawdown"),
                    "exp_b": t2.get("max_drawdown"),
                    "diff": (t2.get("max_drawdown", 0) or 0) - (t1.get("max_drawdown", 0) or 0),
                },
                "turnover": {
                    "exp_a": t1.get("turnover"),
                    "exp_b": t2.get("turnover"),
                    "diff": (t2.get("turnover", 0) or 0) - (t1.get("turnover", 0) or 0),
                },
                "transaction_cost_pct": {
                    "exp_a": c1.get("transaction_cost_pct"),
                    "exp_b": c2.get("transaction_cost_pct"),
                    "diff": (c2.get("transaction_cost_pct", 0) or 0) - (c1.get("transaction_cost_pct", 0) or 0),
                },
            },
            "summary_statement": (
                f"Experiment {exp2.experiment_id} relative to {exp1.experiment_id}: "
                f"Sharpe diff = {(t2.get('sharpe', 0) or 0) - (t1.get('sharpe', 0) or 0):+.2f}, "
                f"CAGR diff = {(t2.get('cagr', 0) or 0) - (t1.get('cagr', 0) or 0):+.2%}."
            )
        }
        return comparison
