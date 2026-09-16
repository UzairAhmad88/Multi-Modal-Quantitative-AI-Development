"""
Experiment Generator and Batch Runner for Research Intelligence.
Generates controlled experiment matrices, hyperparameter grid/random searches,
and executes batch research studies under resource limits.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import itertools
import random
from research_intelligence.experiment_manager.manager import (
    IntelExperimentManager,
    ExperimentConfig,
    ExperimentPriority,
    ExperimentRecord,
)
from research_intelligence.experiment_runner.runner import IntelExperimentRunner


@dataclass
class SearchSpace:
    lookback: List[int] = field(default_factory=lambda: [10, 20, 50])
    learning_rate: List[float] = field(default_factory=lambda: [0.001, 0.01])
    hidden_size: List[int] = field(default_factory=lambda: [32, 64])
    dropout: List[float] = field(default_factory=lambda: [0.1, 0.2])
    signal_threshold: List[float] = field(default_factory=lambda: [0.5, 0.6])
    max_trials: int = 10
    max_runtime_sec: int = 600


class ExperimentGenerator:
    """Generates controlled single-variable experiment variations or grid/random parameter combinations."""

    @staticmethod
    def generate_controlled_pair(
        base_config: ExperimentConfig,
        modified_feature: str,
        hypothesis_id: str,
    ) -> List[ExperimentConfig]:
        """Generates a pair of experiments where only 1 variable (e.g. feature addition) differs."""
        config_a = ExperimentConfig(
            name=f"{base_config.name}_Control",
            hypothesis_id=hypothesis_id,
            dataset=base_config.dataset,
            features=list(base_config.features),
            model=base_config.model,
            validation=dict(base_config.validation),
            backtest=dict(base_config.backtest),
            portfolio=dict(base_config.portfolio),
            risk=dict(base_config.risk),
        )

        new_features = list(base_config.features)
        if modified_feature in new_features:
            new_features.remove(modified_feature)
        else:
            new_features.append(modified_feature)

        config_b = ExperimentConfig(
            name=f"{base_config.name}_Treatment_{modified_feature}",
            hypothesis_id=hypothesis_id,
            dataset=base_config.dataset,
            features=new_features,
            model=base_config.model,
            validation=dict(base_config.validation),
            backtest=dict(base_config.backtest),
            portfolio=dict(base_config.portfolio),
            risk=dict(base_config.risk),
        )
        return [config_a, config_b]

    @staticmethod
    def generate_grid_configs(
        base_config: ExperimentConfig,
        search_space: SearchSpace,
        hypothesis_id: str,
    ) -> List[ExperimentConfig]:
        """Generates grid search experiment configurations up to max_trials limit."""
        keys = ["lookback", "learning_rate", "hidden_size", "dropout", "signal_threshold"]
        values = [
            search_space.lookback,
            search_space.learning_rate,
            search_space.hidden_size,
            search_space.dropout,
            search_space.signal_threshold,
        ]

        combos = list(itertools.product(*values))
        if len(combos) > search_space.max_trials:
            combos = combos[: search_space.max_trials]

        configs = []
        for idx, combo in enumerate(combos):
            param_dict = dict(zip(keys, combo))
            cfg = ExperimentConfig(
                name=f"{base_config.name}_Trial_{idx+1}",
                hypothesis_id=hypothesis_id,
                dataset=base_config.dataset,
                features=list(base_config.features),
                model=base_config.model,
                validation={"hyperparams": param_dict},
                backtest=dict(base_config.backtest),
                portfolio=dict(base_config.portfolio),
                risk=dict(base_config.risk),
            )
            configs.append(cfg)
        return configs


class ResearchBatchRunner:
    """Manages batch research execution containing multiple controlled experiments."""

    def __init__(self, manager: IntelExperimentManager, runner: IntelExperimentRunner):
        self.manager = manager
        self.runner = runner

    def run_batch(
        self,
        batch_name: str,
        configs: List[ExperimentConfig],
        priority: ExperimentPriority = ExperimentPriority.NORMAL,
        auto_approve: bool = True,
    ) -> Dict[str, Any]:
        records: List[ExperimentRecord] = []
        for cfg in configs:
            rec = self.manager.create_experiment(cfg, priority=priority, auto_approve=auto_approve)
            records.append(rec)

        results = []
        for rec in records:
            res = self.runner.run_experiment(rec.experiment_id)
            results.append({"experiment_id": rec.experiment_id, "name": rec.config.name, "results": res})

        return {
            "batch_name": batch_name,
            "total_experiments": len(records),
            "executed": len(results),
            "results": results,
        }
