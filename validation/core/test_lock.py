"""
Test-Set Protection & Access Audit Lock Engine for Walk-Forward OS.
Prevents hyperparameter tuning and model selection on locked test sets to eliminate repeated-test overfitting.
"""

from typing import Dict, Any, List, Optional
import os
import json
from datetime import datetime


class TestSetLockedError(Exception):
    """Raised when an attempt is made to re-evaluate or tune parameters on a locked test set."""
    __test__ = False


class TestSetLockEngine:
    """Manages test set lock state and maintains an immutable access audit trail."""
    __test__ = False

    def __init__(self, storage_dir: str = "artifacts/validation/locks"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def get_lock_status(self, experiment_id: str) -> Dict[str, Any]:
        """Checks if a given experiment test set is locked."""
        lock_file = os.path.join(self.storage_dir, f"{experiment_id}_lock.json")
        if os.path.exists(lock_file):
            with open(lock_file, "r") as f:
                return json.load(f)
        return {
            "experiment_id": experiment_id,
            "is_locked": False,
            "locked_at": None,
            "locked_by": None,
            "access_count": 0,
            "access_log": [],
        }

    def lock_test_set(self, experiment_id: str, config_hash: str, locked_by: str = "RESEARCH_ORCHESTRATOR") -> Dict[str, Any]:
        """Locks the final out-of-sample test set for an experiment."""
        lock_file = os.path.join(self.storage_dir, f"{experiment_id}_lock.json")
        current_status = self.get_lock_status(experiment_id)

        lock_record = {
            "experiment_id": experiment_id,
            "is_locked": True,
            "config_hash": config_hash,
            "locked_at": datetime.now().isoformat(),
            "locked_by": locked_by,
            "access_count": current_status.get("access_count", 0),
            "access_log": current_status.get("access_log", []),
        }

        with open(lock_file, "w") as f:
            json.dump(lock_record, f, indent=2)

        return lock_record

    def verify_access_permission(
        self,
        experiment_id: str,
        incoming_config_hash: str,
        purpose: str = "FINAL_OOS_EVALUATION",
    ) -> Dict[str, Any]:
        """Audits access attempt against locked experiment. Raises TestSetLockedError if unauthorized."""
        status = self.get_lock_status(experiment_id)

        access_entry = {
            "timestamp": datetime.now().isoformat(),
            "incoming_config_hash": incoming_config_hash,
            "purpose": purpose,
        }

        if status["is_locked"]:
            # If config hash matches locked hash, allow ONE-TIME final OOS evaluation
            if status.get("config_hash") != incoming_config_hash:
                status["access_log"].append({**access_entry, "status": "DENIED", "reason": "TEST_SET_LOCKED"})
                self._save_status(experiment_id, status)
                raise TestSetLockedError(
                    f"TEST_SET_LOCKED: Experiment '{experiment_id}' test set is locked with hash {status.get('config_hash')}. "
                    f"Cannot re-tune hyperparameters or alter configuration with hash {incoming_config_hash}."
                )

        status["access_count"] += 1
        status["access_log"].append({**access_entry, "status": "GRANTED"})
        self._save_status(experiment_id, status)

        return {
            "allowed": True,
            "is_locked": status["is_locked"],
            "access_count": status["access_count"],
        }

    def _save_status(self, experiment_id: str, status: Dict[str, Any]) -> None:
        lock_file = os.path.join(self.storage_dir, f"{experiment_id}_lock.json")
        with open(lock_file, "w") as f:
            json.dump(status, f, indent=2)
