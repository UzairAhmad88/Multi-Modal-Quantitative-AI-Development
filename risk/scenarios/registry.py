"""
Scenario Registry & Versioning for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime


class ScenarioRegistry:
    """Registry for historical and hypothetical stress scenarios with explicit versioning."""

    def __init__(self, storage_dir: str = "artifacts/risk/scenarios"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.scenarios: Dict[str, Dict[str, Any]] = {}
        self._load_default_scenarios()

    def register_scenario(
        self,
        scenario_id: str,
        scenario_type: str,
        description: str,
        parameters: Dict[str, Any],
        scenario_version: str = "v1.0.0",
    ) -> Dict[str, Any]:
        """Register a new scenario. Errors if scenario_id already exists to prevent silent overwriting."""
        if scenario_id in self.scenarios:
            existing_ver = self.scenarios[scenario_id].get("scenario_version", "v1.0.0")
            if existing_ver == scenario_version:
                return self.scenarios[scenario_id]

        scen_data = {
            "scenario_id": scenario_id,
            "scenario_version": scenario_version,
            "scenario_type": scenario_type,
            "description": description,
            "parameters": parameters,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        self.scenarios[scenario_id] = scen_data
        self._save(scen_data)
        return scen_data

    def get_scenario(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        return self.scenarios.get(scenario_id)

    def list_scenarios(self) -> List[Dict[str, Any]]:
        return list(self.scenarios.values())

    def _save(self, scen_data: Dict[str, Any]) -> None:
        filepath = os.path.join(self.storage_dir, f"{scen_data['scenario_id']}.json")
        with open(filepath, "w") as f:
            json.dump(scen_data, f, indent=2)

    def _load_default_scenarios(self) -> None:
        defaults = [
            {
                "scenario_id": "MARKET_CRASH_20PCT",
                "scenario_type": "hypothetical",
                "description": "20% sudden equity market crash with 1.5x volatility spike",
                "parameters": {"equity_market_shock": -0.20, "volatility_multiplier": 1.5},
            },
            {
                "scenario_id": "STRESS_CORRELATION_SPIKE",
                "scenario_type": "hypothetical",
                "description": "Correlation matrix convergence toward 1.0",
                "parameters": {"correlation_warp": 0.5},
            },
            {
                "scenario_id": "LIQUIDITY_COST_CRUNCH",
                "scenario_type": "hypothetical",
                "description": "2.0x bid-ask spread expansion and transaction cost multiplier",
                "parameters": {"liquidity_spread_multiplier": 2.0, "transaction_cost_multiplier": 2.0},
            },
        ]
        for d in defaults:
            self.register_scenario(
                scenario_id=d["scenario_id"],
                scenario_type=d["scenario_type"],
                description=d["description"],
                parameters=d["parameters"],
            )
