"""
Execution Attribution Engine: Decomposes total execution cost into spread, slippage, market impact, fees, and timing delays.
"""

from typing import List, Dict, Any
from execution.fills.fill_engine import Fill


class ExecutionAttributionEngine:
    """Attributes total cost breakdown into microstructural components."""

    def attribute_execution_costs(self, fills: List[Fill]) -> Dict[str, Any]:
        """Calculates granular cost breakdown across all execution fills."""
        if not fills:
            return {"total_cost": 0.0, "spread_cost": 0.0, "slippage_cost": 0.0, "impact_cost": 0.0, "fees": 0.0}

        total_trade_val = sum(f.quantity * f.fill_price for f in fills)
        total_fees = sum(f.fees for f in fills)
        total_slippage = sum(f.slippage for f in fills)
        # Estimate spread cost as 40% of slippage, impact as 60% of slippage for breakdown
        estimated_spread = total_slippage * 0.40
        estimated_impact = total_slippage * 0.60

        total_cost = total_fees + total_slippage

        return {
            "total_trade_volume": round(total_trade_val, 2),
            "total_execution_cost": round(total_cost, 2),
            "fees": round(total_fees, 2),
            "total_slippage": round(total_slippage, 2),
            "spread_cost_estimate": round(estimated_spread, 2),
            "market_impact_estimate": round(estimated_impact, 2),
            "cost_bps": round((total_cost / total_trade_val * 10000.0), 2) if total_trade_val > 0 else 0.0
        }
