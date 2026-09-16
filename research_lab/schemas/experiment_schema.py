"""
Standardized Experiment Dataclass Schema & Serialization.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json
from research_lab.experiments.states import ExperimentStatus


@dataclass
class Experiment:
    experiment_id: str
    name: str
    description: str
    hypothesis: Dict[str, str]
    dataset_id: str
    feature_version: str
    model_version: str
    strategy_id: str
    portfolio_config: Dict[str, Any]
    execution_config: Dict[str, Any]
    evaluation_config: Dict[str, Any]
    random_seed: int = 42
    status: ExperimentStatus = ExperimentStatus.DRAFT
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    configuration_hash: str = ""

    def compute_config_hash(self) -> str:
        """Computes deterministic SHA256 configuration hash."""
        config_data = {
            "name": self.name,
            "dataset_id": self.dataset_id,
            "feature_version": self.feature_version,
            "model_version": self.model_version,
            "strategy_id": self.strategy_id,
            "portfolio": self.portfolio_config,
            "execution": self.execution_config,
            "evaluation": self.evaluation_config,
            "random_seed": self.random_seed
        }
        raw_str = json.dumps(config_data, sort_keys=True)
        self.configuration_hash = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()[:16]
        return self.configuration_hash

    def to_dict(self) -> Dict[str, Any]:
        if not self.configuration_hash:
            self.compute_config_hash()
        data = asdict(self)
        data["status"] = self.status.value if hasattr(self.status, "value") else str(self.status)
        return data
