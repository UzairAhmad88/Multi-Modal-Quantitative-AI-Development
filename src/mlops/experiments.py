"""
Experiment Manager Module
Tracks research experiment runs, lifecycle status, Git commit metadata, hardware environment info,
and configuration parameters.
"""

from datetime import datetime, timezone
import uuid
import os
import subprocess
import platform
import sys
from typing import Dict, List, Any, Optional


class ExperimentManager:
    """Quantitative Research Experiment Tracking Manager."""

    def __init__(self, experiment_name: str = "Multimodal_Quant_Experiment"):
        self.experiment_name = experiment_name
        self.experiments: Dict[str, Dict[str, Any]] = {}
        self.runs: Dict[str, Dict[str, Any]] = {}

    def create_experiment(
        self, name: str, description: str = "", config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a top-level experiment container."""
        exp_id = f"EXP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        git_info = self._get_git_info()
        env_info = self._get_environment_info()

        exp_record = {
            "experiment_id": exp_id,
            "experiment_name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "PLANNED",
            "description": description,
            "config": config or {},
            "git_commit": git_info.get("commit_hash", "UNKNOWN"),
            "git_branch": git_info.get("branch", "main"),
            "git": git_info,
            "hardware_metadata": env_info,
            "environment": env_info,
            "runs": []
        }
        self.experiments[exp_id] = exp_record
        return exp_record

    def list_experiments(self) -> List[Dict[str, Any]]:
        """List all experiments or runs."""
        if self.experiments:
            return list(self.experiments.values())
        return list(self.runs.values())

    def get_experiment(self, exp_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve experiment by ID."""
        if exp_id in self.experiments:
            return self.experiments[exp_id]
        if exp_id in self.runs:
            return self.runs[exp_id]
        return None

    def start_run(
        self, exp_id_or_config: Any, config_or_desc: Any = None, description: str = ""
    ) -> Dict[str, Any]:
        """
        Create and record a new research experiment run in RUNNING state.
        """
        if isinstance(exp_id_or_config, str) and exp_id_or_config in self.experiments:
            exp_id = exp_id_or_config
            config = config_or_desc or self.experiments[exp_id].get("config", {})
        else:
            exp_id = "EXP-RUN-GENERIC"
            config = exp_id_or_config if isinstance(exp_id_or_config, dict) else {}

        run_id = f"EXP-RUN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        git_info = self._get_git_info()
        env_info = self._get_environment_info()

        run_record = {
            "run_id": run_id,
            "experiment_id": exp_id,
            "experiment_name": self.experiment_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "RUNNING",
            "description": description,
            "config": config,
            "git": git_info,
            "environment": env_info,
            "random_seed": config.get("random_seed", config.get("seed", 42)),
            "metrics": {},
            "artifacts": [],
            "error": None,
        }
        self.runs[run_id] = run_record
        if exp_id in self.experiments:
            self.experiments[exp_id]["status"] = "RUNNING"
            self.experiments[exp_id]["runs"].append(run_record)

        return run_record

    def log_metrics(self, run_id: str, metrics: Dict[str, Any]):
        """Attach calculated metrics payload to an active run."""
        if run_id in self.runs:
            self.runs[run_id]["metrics"].update(metrics)

    def finish_run(self, run_id: str, metrics: Optional[Dict[str, Any]] = None, status: str = "COMPLETED", error_msg: Optional[str] = None) -> Dict[str, Any]:
        """Mark run as COMPLETED or FAILED."""
        if run_id in self.runs:
            if metrics:
                self.runs[run_id]["metrics"].update(metrics)
            self.runs[run_id]["status"] = status
            self.runs[run_id]["finished_at"] = datetime.now(timezone.utc).isoformat()
            if error_msg:
                self.runs[run_id]["error"] = error_msg

            exp_id = self.runs[run_id].get("experiment_id")
            if exp_id in self.experiments:
                self.experiments[exp_id]["status"] = status
            return self.runs[run_id]
        return {"run_id": run_id, "status": status}

    @staticmethod
    def _get_git_info() -> Dict[str, Any]:
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
            status_out = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
            return {
                "commit_hash": commit,
                "branch": branch,
                "dirty_state": bool(len(status_out) > 0),
            }
        except Exception:
            return {
                "commit_hash": "UNKNOWN_GIT_COMMIT",
                "branch": "main",
                "dirty_state": False,
            }

    @staticmethod
    def _get_environment_info() -> Dict[str, Any]:
        return {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "processor": platform.processor() or "x86_64",
        }
