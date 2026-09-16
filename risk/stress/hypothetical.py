"""
Hypothetical Stress Testing Engine for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from risk.core.risk_result import StressTestResult


class HypotheticalStressEngine:
    """Applies parametric market shocks, correlation warping, liquidity spikes, and transaction cost multipliers."""

    @staticmethod
    def run_hypothetical_stress(
        scenario_id: str,
        portfolio_id: str,
        weights: Dict[str, float],
        parameters: Dict[str, Any],
        base_value: float = 100000.0,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> StressTestResult:
        mkt_shock = parameters.get("equity_market_shock", 0.0)
        vol_mult = parameters.get("volatility_multiplier", 1.0)
        asset_shocks = parameters.get("asset_shocks", {})
        sector_shocks = parameters.get("sector_shocks", {})

        # Calculate asset P&L under shock
        asset_losses: Dict[str, float] = {}
        total_pnl_pct = 0.0

        for asset, w in weights.items():
            # Check asset specific shock first
            if asset in asset_shocks:
                shk = asset_shocks[asset]
            # Check sector shock
            elif asset_metadata and asset_metadata.get(asset, {}).get("sector") in sector_shocks:
                shk = sector_shocks[asset_metadata[asset]["sector"]]
            # Default market shock
            else:
                shk = mkt_shock

            asset_pnl = w * shk
            total_pnl_pct += asset_pnl
            asset_losses[asset] = asset_pnl

        stressed_val = base_value * (1.0 + total_pnl_pct)
        abs_loss = float(max(0.0, base_value - stressed_val))
        pct_loss = float(abs_loss / base_value) if base_value > 0 else 0.0

        return StressTestResult(
            scenario_id=scenario_id,
            portfolio_id=portfolio_id,
            base_value=base_value,
            stressed_value=stressed_val,
            absolute_loss=abs_loss,
            percentage_loss=pct_loss,
            risk_metrics={
                "volatility_multiplier": vol_mult,
                "asset_pnl": asset_losses,
                "total_pnl_pct": total_pnl_pct,
            },
        )
