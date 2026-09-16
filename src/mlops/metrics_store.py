"""
Unified Metric Store Module
Stores namespaced quantitative research metrics (predictive, trading, portfolio, risk, robustness).
"""

from typing import Dict, List, Any, Optional


class MetricStore:
    """Quantitative Namespaced Metrics Store Engine."""

    def __init__(self):
        self.store: Dict[str, Dict[str, Any]] = {}

    def log_metrics(
        self,
        run_id: str,
        metrics_dict_or_predictive: Optional[Dict[str, float]] = None,
        trading_metrics: Optional[Dict[str, float]] = None,
        portfolio_metrics: Optional[Dict[str, float]] = None,
        risk_metrics: Optional[Dict[str, float]] = None,
        robustness_metrics: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Record namespaced metrics for a research run.
        Supports both direct dict with namespaced keys ('predictive.rmse') or separate kwargs.
        """
        if isinstance(metrics_dict_or_predictive, dict) and trading_metrics is None:
            raw_metrics = metrics_dict_or_predictive
            self.store[run_id] = raw_metrics
            return raw_metrics

        metrics_payload = {
            "predictive": metrics_dict_or_predictive or {},
            "trading": trading_metrics or {},
            "portfolio": portfolio_metrics or {},
            "risk": risk_metrics or {},
            "robustness": robustness_metrics or {},
        }
        self.store[run_id] = metrics_payload
        return metrics_payload

    def get_run_metrics(self, run_id: str) -> Dict[str, Any]:
        return self.store.get(run_id, {})

    def get_metrics(self, run_id: str) -> Dict[str, Any]:
        """Retrieve namespaced metrics payload for a run."""
        return self.store.get(run_id, {})
