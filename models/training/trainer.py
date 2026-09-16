"""
Model Training Engine for Quantitative AI Models.
Automates model training, seed fixing, device detection, checkpoint saving, metric tracking, and registry registration.
"""

from typing import Dict, Any, Optional
import time
import os
import torch
import numpy as np
import pandas as pd
from pathlib import Path

from models.factory.factory import ModelFactory
from models.registry.registry import ModelRegistry, ModelStatus
from models.evaluation.evaluator import ModelEvaluator


class ModelTrainingEngine:
    """Orchestrates model training, evaluation, checkpoint saving, and registry integration."""

    def __init__(self, artifact_dir: str = "models/trained", registry_file: str = "artifacts/model_factory_registry.json"):
        self.artifact_dir = Path(artifact_dir)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.registry = ModelRegistry(registry_file=registry_file)
        self.evaluator = ModelEvaluator()

    def train_model(
        self,
        config: Dict[str, Any],
        train_data: Optional[pd.DataFrame] = None,
        val_data: Optional[pd.DataFrame] = None,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Trains model according to YAML config."""
        seed = config.get("training", {}).get("seed", 42)
        np.random.seed(seed)
        torch.manual_seed(seed)

        # 1. Instantiate via factory
        model = ModelFactory.create_model(config, model_id=model_id)

        # 2. Register initial state
        self.registry.register_model(
            model_id=model.model_id,
            name=model.name,
            version=model.version,
            model_type=config.get("model", {}).get("type", "regression"),
            task=config.get("model", {}).get("task", "regression"),
            config=config,
            status=ModelStatus.TRAINING
        )

        start_time = time.time()

        # Generate synthetic data if none provided
        if train_data is None or train_data.empty:
            X_train, y_train, X_val, y_val = self._generate_synthetic_training_data()
        else:
            target_col = "returns" if "returns" in train_data.columns else train_data.columns[-1]
            feature_cols = [c for c in train_data.columns if c != target_col]
            X_train = train_data[feature_cols].values
            y_train = train_data[target_col].values
            if val_data is not None and not val_data.empty:
                X_val = val_data[feature_cols].values
                y_val = val_data[target_col].values
            else:
                X_val, y_val = X_train, y_train

        # 3. Execute fit
        model.fit(X_train, y_train)
        duration = time.time() - start_time

        # 4. Evaluate metrics
        eval_results = self.evaluator.evaluate_model(model, X_val, y_val, task=config.get("model", {}).get("task", "regression"))

        # 5. Save artifact
        model_path = self.artifact_dir / f"{model.model_id}.pkl"
        artifact_path = model.save(str(model_path))

        # 6. Update registry
        self.registry.update_model_status(model.model_id, ModelStatus.VALIDATION, metrics=eval_results)
        self.registry._data["models"][model.model_id]["artifact_path"] = artifact_path
        self.registry._save()

        return {
            "status": "COMPLETED",
            "model_id": model.model_id,
            "name": model.name,
            "version": model.version,
            "training_duration_seconds": round(duration, 2),
            "artifact_path": artifact_path,
            "metrics": eval_results
        }

    def _generate_synthetic_training_data(self):
        """Generates synthetic dataset for model training."""
        np.random.seed(42)
        n_train = 200
        n_val = 50
        n_features = 16

        X_tr = np.random.normal(0, 1, (n_train, n_features))
        y_tr = 0.3 * X_tr[:, 0] - 0.2 * X_tr[:, 1] + np.random.normal(0, 0.05, n_train)

        X_v = np.random.normal(0, 1, (n_val, n_features))
        y_v = 0.3 * X_v[:, 0] - 0.2 * X_v[:, 1] + np.random.normal(0, 0.05, n_val)

        return X_tr, y_tr, X_v, y_v
