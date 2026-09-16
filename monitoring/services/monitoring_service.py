"""
Unified Monitoring Service managing audit persistence and artifact generation.
"""

import json
import os
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..core.monitor_engine import ModelMonitorEngine
from ..core.monitor_result import MonitoringResult


class MonitoringService:
    """Service layer managing Model Monitoring runs, persistence, and reporting."""

    def __init__(self, artifacts_dir: Optional[str] = None):
        if artifacts_dir is None:
            artifacts_dir = os.path.join(os.getcwd(), "artifacts", "monitoring")
        self.artifacts_dir = Path(artifacts_dir)
        self.runs_dir = self.artifacts_dir / "runs"
        self.reports_dir = self.artifacts_dir / "reports"

        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.engine = ModelMonitorEngine()

    def run_monitoring(
        self,
        experiment_id: str = "EXP-001",
        baseline_df: Optional[pd.DataFrame] = None,
        target_df: Optional[pd.DataFrame] = None,
        baseline_predictions: Optional[np.ndarray] = None,
        target_predictions: Optional[np.ndarray] = None,
        baseline_signals: Optional[np.ndarray] = None,
        target_signals: Optional[np.ndarray] = None,
        baseline_returns: Optional[np.ndarray] = None,
        target_returns: Optional[np.ndarray] = None,
        feature_columns: Optional[List[str]] = None,
    ) -> MonitoringResult:
        # Create synthetic datasets if not provided
        if baseline_df is None:
            np.random.seed(42)
            n_samples = 250
            baseline_df = pd.DataFrame({
                "market_volatility": np.random.normal(0.015, 0.005, n_samples),
                "news_sentiment": np.random.normal(0.10, 0.20, n_samples),
                "sec_pe_ratio": np.random.normal(20.0, 3.0, n_samples),
                "alpha_score": np.random.normal(0.02, 0.01, n_samples),
            })
            baseline_predictions = np.random.normal(0.01, 0.02, n_samples)
            baseline_signals = np.random.normal(0.05, 0.10, n_samples)
            baseline_returns = np.random.normal(0.0005, 0.01, n_samples)

        if target_df is None:
            np.random.seed(99)
            n_samples = 250
            target_df = pd.DataFrame({
                "market_volatility": np.random.normal(0.025, 0.008, n_samples),  # Drifted
                "news_sentiment": np.random.normal(0.05, 0.25, n_samples),
                "sec_pe_ratio": np.random.normal(20.2, 3.1, n_samples),
                "alpha_score": np.random.normal(0.015, 0.012, n_samples),
            })
            target_predictions = np.random.normal(0.005, 0.025, n_samples)
            target_signals = np.random.normal(0.03, 0.12, n_samples)
            target_returns = np.random.normal(0.0001, 0.015, n_samples)

        result = self.engine.run_monitoring_audit(
            experiment_id=experiment_id,
            baseline_df=baseline_df,
            target_df=target_df,
            baseline_predictions=baseline_predictions,
            target_predictions=target_predictions,
            baseline_signals=baseline_signals,
            target_signals=target_signals,
            baseline_returns=baseline_returns,
            target_returns=target_returns,
            feature_columns=feature_columns,
        )

        # Save result JSON
        run_file = self.runs_dir / f"{result.monitoring_id}.json"
        with open(run_file, "w") as f:
            f.write(result.model_dump_json(indent=2))

        return result

    def get_monitoring_run(self, monitoring_id: str) -> Optional[MonitoringResult]:
        run_file = self.runs_dir / f"{monitoring_id}.json"
        if not run_file.exists():
            # Search by prefix or list all
            for f in self.runs_dir.glob("*.json"):
                if monitoring_id in f.name:
                    with open(f, "r") as fp:
                        return MonitoringResult.model_validate_json(fp.read())
            return None

        with open(run_file, "r") as fp:
            return MonitoringResult.model_validate_json(fp.read())

    def list_monitoring_runs(self) -> List[Dict[str, Any]]:
        runs = []
        for f in sorted(self.runs_dir.glob("*.json"), key=os.path.getmtime, reverse=True):
            try:
                with open(f, "r") as fp:
                    data = json.load(fp)
                    runs.append({
                        "monitoring_id": data.get("monitoring_id"),
                        "experiment_id": data.get("experiment_id"),
                        "timestamp": data.get("timestamp"),
                        "status": data.get("health_score", {}).get("status"),
                        "overall_health_score": data.get("health_score", {}).get("overall_health_score"),
                    })
            except Exception:
                continue
        return runs
