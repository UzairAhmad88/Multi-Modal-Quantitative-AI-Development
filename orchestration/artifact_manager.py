"""
Artifact Manager for Experiment Runs.
Maintains artifact directory tree and produces manifest.json per experiment run.
"""

import os
import json
from typing import Dict, Any
import datetime


class ArtifactManager:
    """Manages creation, directory mapping, and manifest registry for run artifacts."""

    CATEGORIES = [
        "experiments", "models", "datasets", "predictions", "signals",
        "portfolios", "backtests", "validation", "reports", "logs"
    ]

    def __init__(self, base_dir: str = "artifacts"):
        self.base_dir = base_dir
        self._ensure_directories()

    def _ensure_directories(self):
        for cat in self.CATEGORIES:
            os.makedirs(os.path.join(self.base_dir, cat), exist_ok=True)

    def register_artifact_manifest(
        self,
        experiment_id: str,
        run_id: str,
        dataset: str,
        features: list,
        model: str,
        backtest: Dict[str, Any],
        validation: Dict[str, Any],
        report_path: str,
    ) -> str:
        run_dir = os.path.join(self.base_dir, f"runs/{run_id}")
        os.makedirs(run_dir, exist_ok=True)

        manifest = {
            "experiment_id": experiment_id,
            "run_id": run_id,
            "dataset": dataset,
            "features": features,
            "model": model,
            "backtest": backtest,
            "validation": validation,
            "report_path": report_path,
            "created_at": datetime.datetime.utcnow().isoformat(),
        }

        manifest_path = os.path.join(run_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest_path
