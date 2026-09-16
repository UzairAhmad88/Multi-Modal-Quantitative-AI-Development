"""
Unified Walk-Forward & OOS Service for Walk-Forward OS.
Handles experiment storage, report generation, and API integration.
"""

from typing import Dict, Any, List, Optional
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime

from validation.core.validation_engine import AdvancedWalkForwardEngine
from validation.core.validation_result import ValidationResult


class WalkForwardService:
    """Service layer managing walk-forward validation runs and artifact persistence."""

    def __init__(self, storage_dir: str = "artifacts/validation"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "runs"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_dir, "reports"), exist_ok=True)
        self.engine = AdvancedWalkForwardEngine(storage_dir=self.storage_dir)

    def run_walk_forward(
        self,
        experiment_id: str = "EXP-001",
        method: str = "EXPANDING",
        train_window_size: int = 250,
        val_window_size: int = 50,
        test_window_size: int = 50,
        step_size: int = 50,
        purge_period: int = 5,
        embargo_period: int = 5,
        lock_test_set: bool = False,
        sample_size: int = 500,
    ) -> Dict[str, Any]:
        """Generates synthetic dataset and runs full walk-forward validation."""
        np.random.seed(42)
        dates = pd.date_range("2022-01-01", periods=sample_size, freq="B")
        df = pd.DataFrame({
            "timestamp": dates.strftime("%Y-%m-%d"),
            "availability_timestamp": (dates - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            "feature_1": np.random.normal(0, 1, size=sample_size),
            "feature_2": np.random.normal(0, 1, size=sample_size),
            "target": np.random.normal(0.0005, 0.012, size=sample_size),
        })

        res = self.engine.run_walk_forward_experiment(
            experiment_id=experiment_id,
            df=df,
            method=method,
            train_window_size=train_window_size,
            val_window_size=val_window_size,
            test_window_size=test_window_size,
            step_size=step_size,
            purge_period=purge_period,
            embargo_period=embargo_period,
            timestamp_col="timestamp",
            target_col="target",
            lock_test_set=lock_test_set,
        )

        res_dict = res.to_dict()
        res_clean = self._make_json_serializable(res_dict)
        self._save_run(res_clean)

        return res_clean

    def get_run(self, validation_id: str) -> Optional[Dict[str, Any]]:
        filepath = os.path.join(self.storage_dir, "runs", f"{validation_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as f:
            return json.load(f)

    @staticmethod
    def _make_json_serializable(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: WalkForwardService._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [WalkForwardService._make_json_serializable(v) for v in obj]
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    def _save_run(self, res_dict: Dict[str, Any]) -> None:
        filepath = os.path.join(self.storage_dir, "runs", f"{res_dict['validation_id']}.json")
        with open(filepath, "w") as f:
            json.dump(res_dict, f, indent=2)
