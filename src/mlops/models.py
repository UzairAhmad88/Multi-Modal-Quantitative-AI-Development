"""
Model Registry & Artifact Management Module
Persists trained model artifacts, scalers, and metadata in artifacts/models/<name>/<version>/ and manages model promotion lifecycles.
"""

from datetime import datetime, timezone
import json
import os
import shutil
from typing import Dict, List, Any, Optional, Tuple


class ModelRegistry:
    """Quantitative Model Registry & Promotion Lifecycle Manager."""

    VALID_LIFECYCLE_STATES = ["EXPERIMENTAL", "VALIDATED", "PAPER", "ARCHIVED"]

    def __init__(self, storage_dir: str = "artifacts/models"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.models: Dict[str, Dict[str, Any]] = {}

    def register_model(
        self,
        model_name: str,
        version: str = "v1.0.0",
        framework: str = "PyTorch",
        feature_names: Optional[List[str]] = None,
        metrics: Optional[Dict[str, float]] = None,
        model_type: Optional[str] = None,
        training_dataset: str = "sp500_daily",
        feature_version: str = "v1.0.0",
        status: str = "EXPERIMENTAL",
        model_object: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Register a trained model version and create artifact storage directory.
        """
        if status not in self.VALID_LIFECYCLE_STATES:
            raise ValueError(f"Invalid status {status}. Must be one of {self.VALID_LIFECYCLE_STATES}")

        eff_type = model_type or model_name
        feat_list = feature_names or []
        metrics_dict = metrics or {}
        model_id = f"MODEL-{model_name.upper()}-{version}"
        artifact_path = os.path.join(self.storage_dir, model_name, version)
        os.makedirs(artifact_path, exist_ok=True)

        model_record = {
            "model_id": model_id,
            "model_name": model_name,
            "model_type": eff_type,
            "version": version,
            "framework": framework,
            "status": status,
            "feature_names": feat_list,
            "feature_count": len(feat_list),
            "training_dataset": training_dataset,
            "dataset_version": training_dataset,
            "feature_version": feature_version,
            "metrics": metrics_dict,
            "artifact_path": artifact_path,
            "signature": {
                "input_features": feat_list,
                "input_shape": [None, len(feat_list)],
                "output_format": "prediction_and_confidence"
            },
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        self.models[model_id] = model_record

        # Save metadata.json & metrics.json inside artifact directory
        with open(os.path.join(artifact_path, "metadata.json"), "w") as f:
            json.dump(model_record, f, indent=2)
        with open(os.path.join(artifact_path, "metrics.json"), "w") as f:
            json.dump(metrics_dict, f, indent=2)

        return model_record

    def list_models(self) -> List[Dict[str, Any]]:
        return list(self.models.values())

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        return self.models.get(model_id)

    def promote_model(self, model_id: str, new_status: str) -> Dict[str, Any]:
        """
        Promote model status: EXPERIMENTAL -> VALIDATED -> PAPER -> ARCHIVED.
        """
        if new_status not in self.VALID_LIFECYCLE_STATES:
            raise ValueError(f"Invalid promotion status: {new_status}")
        if model_id not in self.models:
            raise ValueError(f"Model ID {model_id} not registered")

        self.models[model_id]["status"] = new_status
        self.models[model_id]["promoted_at"] = datetime.now(timezone.utc).isoformat()

        # Update metadata.json on disk
        artifact_path = self.models[model_id]["artifact_path"]
        with open(os.path.join(artifact_path, "metadata.json"), "w") as f:
            json.dump(self.models[model_id], f, indent=2)

        return self.models[model_id]

    def update_status(self, model_id: str, new_status: str) -> Dict[str, Any]:
        return self.promote_model(model_id, new_status)

    def validate_signature(self, model_id: str, input_features: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate input feature names and ordering against registered model signature.
        """
        if model_id not in self.models:
            return False, [f"Model ID {model_id} not found in registry"]

        expected = self.models[model_id]["feature_names"]
        issues = []
        for feat in expected:
            if feat not in input_features:
                issues.append(f"Missing expected feature signature item: {feat}")

        return len(issues) == 0, issues
