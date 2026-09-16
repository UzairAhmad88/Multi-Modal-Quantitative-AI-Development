"""
Central Stress Testing Engine Facade for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from risk.core.risk_result import StressTestResult
from risk.scenarios.registry import ScenarioRegistry
from risk.stress.historical import HistoricalStressEngine
from risk.stress.hypothetical import HypotheticalStressEngine


class StressTestingEngine:
    """Unified Stress Testing Engine managing historical, hypothetical, and composite stress scenarios."""

    def __init__(self, registry: Optional[ScenarioRegistry] = None):
        self.registry = registry or ScenarioRegistry()

    def run_scenario(
        self,
        scenario_id: str,
        portfolio_id: str,
        weights: Dict[str, float],
        base_value: float = 100000.0,
        historical_returns: Optional[np.ndarray] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StressTestResult:
        scen = self.registry.get_scenario(scenario_id)
        if not scen:
            # Fallback inline hypothetical scenario
            scen = {
                "scenario_id": scenario_id,
                "scenario_type": "hypothetical",
                "parameters": {"equity_market_shock": -0.15},
            }

        scen_type = scen.get("scenario_type", "hypothetical")
        params = scen.get("parameters", {})

        if scen_type == "historical" and historical_returns is not None:
            return HistoricalStressEngine.run_historical_stress(
                scenario_id=scenario_id,
                portfolio_id=portfolio_id,
                weights=weights,
                historical_returns=historical_returns,
                base_value=base_value,
            )
        else:
            return HypotheticalStressEngine.run_hypothetical_stress(
                scenario_id=scenario_id,
                portfolio_id=portfolio_id,
                weights=weights,
                parameters=params,
                base_value=base_value,
                asset_metadata=asset_metadata,
            )

    def run_stress_matrix(
        self,
        portfolio_id: str,
        weights: Dict[str, float],
        scenario_ids: Optional[List[str]] = None,
        base_value: float = 100000.0,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Execute a matrix of stress scenarios and return factual results."""
        if not scenario_ids:
            scenarios = self.registry.list_scenarios()
            scenario_ids = [s["scenario_id"] for s in scenarios]

        results = {}
        for s_id in scenario_ids:
            res = self.run_scenario(
                scenario_id=s_id,
                portfolio_id=portfolio_id,
                weights=weights,
                base_value=base_value,
                asset_metadata=asset_metadata,
            )
            results[s_id] = res.to_dict()

        return {
            "portfolio_id": portfolio_id,
            "base_value": base_value,
            "scenario_count": len(results),
            "stress_results": results,
        }
