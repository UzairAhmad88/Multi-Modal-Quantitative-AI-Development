"""
Ablation Engine for Research Intelligence.
Automates multi-modal feature set ablation studies to determine incremental value of modalities.
"""

from typing import Dict, List, Any
from research_intelligence.experiment_manager.manager import (
    IntelExperimentManager,
    ExperimentConfig,
    ExperimentPriority,
)
from research_intelligence.experiment_runner.runner import IntelExperimentRunner


class IntelAblationEngine:
    """Generates and executes modality ablation experiments (Full, No News, No Fundamentals, Market Only)."""

    def __init__(self, manager: IntelExperimentManager, runner: IntelExperimentRunner):
        self.manager = manager
        self.runner = runner

    def run_ablation_study(
        self,
        base_config: ExperimentConfig,
        hypothesis_id: str,
        auto_approve: bool = True,
    ) -> Dict[str, Any]:
        """Generates standard modality ablation configs and runs them."""
        modalities = {
            "FULL": base_config.features,
            "FULL_MINUS_NEWS": [f for f in base_config.features if "news" not in f.lower() and "sentiment" not in f.lower()],
            "FULL_MINUS_FUNDAMENTALS": [f for f in base_config.features if "pe_" not in f.lower() and "pb_" not in f.lower() and "fundamental" not in f.lower()],
            "FULL_MINUS_REGIME": [f for f in base_config.features if "regime" not in f.lower()],
            "MARKET_ONLY": [f for f in base_config.features if "return" in f.lower() or "vol" in f.lower() or "price" in f.lower() or "close" in f.lower() or "sma" in f.lower()],
        }

        ablation_results = {}
        for ab_name, feats in modalities.items():
            if not feats:
                feats = ["market_return"]  # Fallback to market return if empty

            cfg = ExperimentConfig(
                name=f"{base_config.name}_Ablation_{ab_name}",
                hypothesis_id=hypothesis_id,
                dataset=base_config.dataset,
                features=feats,
                model=base_config.model,
                validation=dict(base_config.validation),
                backtest=dict(base_config.backtest),
                portfolio=dict(base_config.portfolio),
                risk=dict(base_config.risk),
            )
            rec = self.manager.create_experiment(cfg, priority=ExperimentPriority.HIGH, auto_approve=auto_approve)
            res = self.runner.run_experiment(rec.experiment_id)
            ablation_results[ab_name] = {
                "experiment_id": rec.experiment_id,
                "features_count": len(feats),
                "features": feats,
                "metrics": res,
            }

        return {
            "study_type": "ABLATION",
            "base_experiment": base_config.name,
            "modality_results": ablation_results,
            "modality_contributions": self._calculate_contributions(ablation_results),
        }

    def _calculate_contributions(self, results: Dict[str, Any]) -> Dict[str, float]:
        full_sharpe = results.get("FULL", {}).get("metrics", {}).get("trading_metrics", {}).get("sharpe", 1.0) or 1.0
        no_news_sharpe = results.get("FULL_MINUS_NEWS", {}).get("metrics", {}).get("trading_metrics", {}).get("sharpe", 1.0) or 1.0
        no_fund_sharpe = results.get("FULL_MINUS_FUNDAMENTALS", {}).get("metrics", {}).get("trading_metrics", {}).get("sharpe", 1.0) or 1.0

        return {
            "news_incremental_sharpe": round(full_sharpe - no_news_sharpe, 4),
            "fundamentals_incremental_sharpe": round(full_sharpe - no_fund_sharpe, 4),
        }
