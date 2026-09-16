"""
Execution Scenario Stress Testing Engine: Evaluates order execution under liquidity dry-ups, volatility spikes, and wide spreads.
"""

from typing import Dict, Any, List


class ExecutionScenarioEngine:
    """Simulates execution behavior under stress scenarios."""

    def __init__(self):
        self.scenarios = {
            "normal": {"volatility_mult": 1.0, "spread_mult": 1.0, "volume_mult": 1.0, "latency_mult": 1.0},
            "low_liquidity": {"volatility_mult": 1.5, "spread_mult": 2.5, "volume_mult": 0.3, "latency_mult": 1.5},
            "high_volatility": {"volatility_mult": 3.0, "spread_mult": 2.0, "volume_mult": 0.8, "latency_mult": 2.0},
            "delayed_execution": {"volatility_mult": 1.0, "spread_mult": 1.2, "volume_mult": 1.0, "latency_mult": 5.0}
        }

    def get_stressed_snapshot(
        self,
        market_snapshot: Dict[str, Any],
        scenario_name: str = "normal"
    ) -> Dict[str, Any]:
        """Applies scenario stress multipliers to base market snapshot."""
        sc = self.scenarios.get(scenario_name, self.scenarios["normal"])
        vol = market_snapshot.get("volatility", 0.02) * sc["volatility_mult"]
        spread = market_snapshot.get("spread_bps", 2.0) * sc["spread_mult"]
        mkt_vol = market_snapshot.get("volume", 100000.0) * sc["volume_mult"]

        stressed = dict(market_snapshot)
        stressed["volatility"] = vol
        stressed["spread_bps"] = spread
        stressed["volume"] = mkt_vol
        stressed["scenario_applied"] = scenario_name
        return stressed
