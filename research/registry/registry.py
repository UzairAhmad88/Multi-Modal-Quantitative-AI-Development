"""
Experiment Registry implementation.
Maintains persistent index of experiments, runs, artifacts, metrics, and models.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ExperimentRegistry:
    """Persistent registry for research experiments and execution runs."""

    def __init__(self, registry_file: str = "artifacts/experiment_registry.json") -> None:
        self.registry_path = Path(registry_file)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load registry from {self.registry_path}: {e}")
        return {
            "experiments": {},
            "runs": {},
            "models": {},
            "datasets": {},
            "updated_at": datetime.utcnow().isoformat()
        }

    def _save(self) -> None:
        self._data["updated_at"] = datetime.utcnow().isoformat()
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def register_experiment(
        self,
        experiment_id: str,
        name: str,
        config: Dict[str, Any],
        tags: Optional[List[str]] = None,
        notes: str = ""
    ) -> None:
        self._data["experiments"][experiment_id] = {
            "experiment_id": experiment_id,
            "name": name,
            "config": config,
            "tags": tags or [],
            "notes": notes,
            "created_at": datetime.utcnow().isoformat(),
            "status": "CONFIGURED",
            "runs": []
        }
        self._save()

    def register_run(
        self,
        run_id: str,
        experiment_id: str,
        config: Dict[str, Any],
        status: str = "PENDING",
        dataset_meta: Optional[Dict[str, Any]] = None,
        model_meta: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        artifacts: Optional[Dict[str, str]] = None
    ) -> None:
        run_entry = {
            "run_id": run_id,
            "experiment_id": experiment_id,
            "status": status,
            "config": config,
            "dataset": dataset_meta or {},
            "model": model_meta or {},
            "metrics": metrics or {},
            "artifacts": artifacts or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self._data["runs"][run_id] = run_entry

        if experiment_id in self._data["experiments"]:
            exp_runs = self._data["experiments"][experiment_id].setdefault("runs", [])
            if run_id not in exp_runs:
                exp_runs.append(run_id)
            self._data["experiments"][experiment_id]["status"] = status

        self._save()

    def update_run_status(
        self,
        run_id: str,
        status: str,
        metrics: Optional[Dict[str, Any]] = None,
        artifacts: Optional[Dict[str, str]] = None,
        error: Optional[str] = None
    ) -> None:
        if run_id in self._data["runs"]:
            self._data["runs"][run_id]["status"] = status
            if metrics:
                self._data["runs"][run_id]["metrics"].update(metrics)
            if artifacts:
                self._data["runs"][run_id]["artifacts"].update(artifacts)
            if error:
                self._data["runs"][run_id]["error"] = error

            exp_id = self._data["runs"][run_id]["experiment_id"]
            if exp_id in self._data["experiments"]:
                self._data["experiments"][exp_id]["status"] = status
            self._save()

    def list_experiments(
        self,
        model: Optional[str] = None,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        dataset: Optional[str] = None,
        name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = []
        for run in self._data["runs"].values():
            if status and run.get("status") != status:
                continue
            if name and name.lower() not in run.get("config", {}).get("experiment", {}).get("name", "").lower():
                continue
            if model and model.lower() not in run.get("config", {}).get("model", {}).get("type", "").lower():
                continue
            if symbol:
                symbols = run.get("config", {}).get("data", {}).get("symbols", [])
                if symbol not in symbols:
                    continue
            if dataset and dataset.lower() not in str(run.get("dataset", {})).lower():
                continue
            results.append(run)
        return results

    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        return self._data["experiments"].get(experiment_id)

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._data["runs"].get(run_id)

    def compare_runs(self, run_id_1: str, run_id_2: str) -> Dict[str, Any]:
        run1 = self.get_run(run_id_1)
        run2 = self.get_run(run_id_2)

        if not run1 or not run2:
            return {"error": "One or both run IDs not found in registry."}

        m1 = run1.get("metrics", {})
        m2 = run2.get("metrics", {})

        metrics_comparison = {
            "CAGR": {"run_1": m1.get("cagr", 0.0), "run_2": m2.get("cagr", 0.0)},
            "Sharpe": {"run_1": m1.get("sharpe", 0.0), "run_2": m2.get("sharpe", 0.0)},
            "Max Drawdown": {"run_1": m1.get("max_drawdown", 0.0), "run_2": m2.get("max_drawdown", 0.0)},
            "Volatility": {"run_1": m1.get("volatility", 0.0), "run_2": m2.get("volatility", 0.0)},
            "Turnover": {"run_1": m1.get("turnover", 0.0), "run_2": m2.get("turnover", 0.0)},
            "Directional Accuracy": {"run_1": m1.get("directional_accuracy", 0.0), "run_2": m2.get("directional_accuracy", 0.0)}
        }

        return {
            "run_1": {"id": run_id_1, "name": run1.get("config", {}).get("experiment", {}).get("name")},
            "run_2": {"id": run_id_2, "name": run2.get("config", {}).get("experiment", {}).get("name")},
            "metrics": metrics_comparison
        }
