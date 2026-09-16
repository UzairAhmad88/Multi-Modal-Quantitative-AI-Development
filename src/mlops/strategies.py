"""
Strategy Registry Module
Versions composite trading strategies bound to dataset, feature, model, portfolio optimizer, risk, and cost specifications.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional


class StrategyRegistry:
    """Quantitative Composite Strategy Registry."""

    def __init__(self):
        self.strategies: Dict[str, Dict[str, Any]] = {}

    def register_strategy(
        self,
        strategy_name: str,
        version: str = "v1.0.0",
        signal_logic: str = "Top decile positive alpha signals",
        portfolio_method: str = "mean_variance",
        dataset_version: str = "v1.0.0",
        feature_version: str = "v1.0.0",
        model_version: str = "v1.0.0",
        portfolio_optimizer: str = "mean_variance",
        risk_config: Optional[Dict[str, Any]] = None,
        cost_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Register a composite quantitative strategy version.
        """
        strategy_id = f"STRAT-{strategy_name.upper()}-{version}"
        strat_record = {
            "strategy_id": strategy_id,
            "strategy_name": strategy_name,
            "version": version,
            "signal_logic": signal_logic,
            "portfolio_method": portfolio_method,
            "dataset_version": dataset_version,
            "feature_version": feature_version,
            "model_version": model_version,
            "portfolio_optimizer": portfolio_optimizer,
            "risk_config": risk_config or {},
            "cost_config": cost_config or {},
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        self.strategies[strategy_id] = strat_record
        return strat_record

    def list_strategies(self) -> List[Dict[str, Any]]:
        return list(self.strategies.values())

    def get_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        return self.strategies.get(strategy_id)
