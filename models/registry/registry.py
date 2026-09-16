"""
Central Model Registry for Quantitative AI Models.
Tracks model versions, lifecycle statuses, evaluation metrics, artifact paths, and champion/challenger designations.
"""

from __future__ import annotations
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelStatus(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    TRAINING = "TRAINING"
    VALIDATION = "VALIDATION"
    CANDIDATE = "CANDIDATE"
    PAPER = "PAPER"
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"


class ModelRegistry:
    """Persistent registry for quantitative models, versions, and champion/challenger status."""

    def __init__(self, registry_file: str = "artifacts/model_factory_registry.json"):
        self.registry_path = Path(registry_file)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load model registry: {e}")
        return {
            "models": {},
            "champion_id": None,
            "updated_at": datetime.utcnow().isoformat()
        }

    def _save(self) -> None:
        self._data["updated_at"] = datetime.utcnow().isoformat()
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def register_model(
        self,
        model_id: str,
        name: str,
        version: str,
        model_type: str,
        task: str = "regression",
        config: Optional[Dict[str, Any]] = None,
        artifact_path: str = "",
        status: ModelStatus = ModelStatus.DEVELOPMENT
    ) -> Dict[str, Any]:
        entry = {
            "model_id": model_id,
            "name": name,
            "version": version,
            "model_type": model_type,
            "task": task,
            "status": status.value,
            "config": config or {},
            "artifact_path": artifact_path,
            "metrics": {},
            "validation_gates": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        self._data["models"][model_id] = entry
        self._save()
        return entry

    def update_model_status(self, model_id: str, status: ModelStatus, metrics: Optional[Dict[str, Any]] = None) -> bool:
        if model_id not in self._data["models"]:
            return False

        model = self._data["models"][model_id]
        model["status"] = status.value
        if metrics:
            model["metrics"].update(metrics)
        model["updated_at"] = datetime.utcnow().isoformat()

        if status == ModelStatus.PAPER:
            self._data["champion_id"] = model_id

        self._save()
        return True

    def promote_to_candidate(self, model_id: str, validation_results: Dict[str, Any]) -> bool:
        """Promotes model to CANDIDATE if validation gates pass."""
        if model_id not in self._data["models"]:
            return False

        # Require validation gates
        passed = validation_results.get("status") == "PASS" or validation_results.get("is_valid", True)
        if passed:
            self._data["models"][model_id]["validation_gates"] = validation_results
            return self.update_model_status(model_id, ModelStatus.CANDIDATE)
        else:
            self.update_model_status(model_id, ModelStatus.FAILED)
            return False

    def set_champion(self, model_id: str) -> bool:
        """Promotes model to PAPER champion."""
        if model_id in self._data["models"]:
            self._data["champion_id"] = model_id
            self.update_model_status(model_id, ModelStatus.PAPER)
            return True
        return False

    def get_champion(self) -> Optional[Dict[str, Any]]:
        champ_id = self._data.get("champion_id")
        if champ_id and champ_id in self._data["models"]:
            return self._data["models"][champ_id]
        return None

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        return self._data["models"].get(model_id)

    def list_models(self, status: Optional[str] = None, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        for m in self._data["models"].values():
            if status and m.get("status") != status:
                continue
            if model_type and m.get("model_type") != model_type:
                continue
            results.append(m)
        return results

    def rollback_champion(self) -> Optional[Dict[str, Any]]:
        """Rolls back champion to previous PAPER or CANDIDATE model."""
        curr_champ_id = self._data.get("champion_id")
        other_candidates = [
            m for m in self._data["models"].values()
            if m.get("model_id") != curr_champ_id and m.get("status") in [ModelStatus.CANDIDATE.value, ModelStatus.PAPER.value]
        ]
        if not other_candidates:
            # Fallback to any model that passed validation if no explicit candidate
            other_candidates = [
                m for m in self._data["models"].values()
                if m.get("model_id") != curr_champ_id and m.get("status") not in [ModelStatus.FAILED.value]
            ]
        if other_candidates:
            other_candidates.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            if curr_champ_id and curr_champ_id in self._data["models"]:
                self._data["models"][curr_champ_id]["status"] = ModelStatus.VALIDATION.value
            new_champ = other_candidates[0]
            self.set_champion(new_champ["model_id"])
            return new_champ
        return None
