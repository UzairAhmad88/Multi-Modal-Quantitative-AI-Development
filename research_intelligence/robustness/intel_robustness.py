"""
Robustness Engine for Research Intelligence.
Evaluates model and strategy performance stability across multiple time periods, transaction costs,
signal thresholds, lookback windows, and market regimes.
"""

from typing import Dict, List, Any
import numpy as np
from research_intelligence.experiment_manager.manager import (
    IntelExperimentManager,
    ExperimentConfig,
    ExperimentPriority,
)
from research_intelligence.experiment_runner.runner import IntelExperimentRunner


class IntelRobustnessEngine:
    """Automates multi-dimensional parameter and market regime stress sweeps."""

    def __init__(self, manager: IntelExperimentManager, runner: IntelExperimentRunner):
        self.manager = manager
        self.runner = runner

    def run_robustness_suite(
        self,
        base_config: ExperimentConfig,
        hypothesis_id: str,
        cost_bps_list: List[float] = [1.0, 5.0, 10.0, 20.0],
        periods: List[str] = ["2018-2020", "2021-2023", "2024-2026"],
        thresholds: List[float] = [0.5, 0.55, 0.6],
        auto_approve: bool = True,
    ) -> Dict[str, Any]:
        """Runs multi-slice robustness tests across costs, periods, and thresholds."""
        cost_results = {}
        for bps in cost_bps_list:
            cfg = ExperimentConfig(
                name=f"{base_config.name}_Cost_{bps}bps",
                hypothesis_id=hypothesis_id,
                dataset=base_config.dataset,
                features=list(base_config.features),
                model=base_config.model,
                backtest={"transaction_cost_bps": bps},
            )
            rec = self.manager.create_experiment(cfg, auto_approve=auto_approve)
            res = self.runner.run_experiment(rec.experiment_id)
            cost_results[f"{bps}_bps"] = res.get("trading_metrics", {}).get("sharpe", 0.0)

        period_results = {}
        for p in periods:
            cfg = ExperimentConfig(
                name=f"{base_config.name}_Period_{p}",
                hypothesis_id=hypothesis_id,
                dataset=f"{base_config.dataset}_{p}",
                features=list(base_config.features),
                model=base_config.model,
            )
            rec = self.manager.create_experiment(cfg, auto_approve=auto_approve)
            res = self.runner.run_experiment(rec.experiment_id)
            period_results[p] = res.get("trading_metrics", {}).get("sharpe", 0.0)

        threshold_results = {}
        for th in thresholds:
            cfg = ExperimentConfig(
                name=f"{base_config.name}_Thresh_{th}",
                hypothesis_id=hypothesis_id,
                dataset=base_config.dataset,
                features=list(base_config.features),
                model=base_config.model,
                validation={"signal_threshold": th},
            )
            rec = self.manager.create_experiment(cfg, auto_approve=auto_approve)
            res = self.runner.run_experiment(rec.experiment_id)
            threshold_results[str(th)] = res.get("trading_metrics", {}).get("sharpe", 0.0)

        sharpes = list(period_results.values())
        stability_score = round(1.0 - (np.std(sharpes) / (np.mean(sharpes) + 1e-6)), 4) if sharpes else 0.0

        return {
            "study_type": "ROBUSTNESS",
            "base_experiment": base_config.name,
            "cost_sensitivity": cost_results,
            "period_breakdown": period_results,
            "threshold_sensitivity": threshold_results,
            "stability_score": max(0.0, float(stability_score)),
        }
