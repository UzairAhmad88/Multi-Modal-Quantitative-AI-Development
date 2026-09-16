"""
Slippage Model Interface for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional


class PortfolioSlippageModel:
    """Estimates expected price slippage per asset based on volatility and participation."""

    @staticmethod
    def estimate_slippage_bps(
        trade_size_usd: float,
        adv_usd: float,
        asset_volatility: float = 0.20,
        base_slippage_bps: float = 5.0,
    ) -> float:
        """Estimate slippage in basis points."""
        if adv_usd <= 0:
            return base_slippage_bps * 2.0

        participation = trade_size_usd / adv_usd
        vol_scaler = asset_volatility / 0.20
        slippage_bps = base_slippage_bps + (100.0 * (participation**0.5) * vol_scaler)
        return float(min(slippage_bps, 200.0))
