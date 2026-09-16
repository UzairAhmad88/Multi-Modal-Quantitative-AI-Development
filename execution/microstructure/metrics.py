"""
Microstructure metrics calculation and liquidity flags.
"""

from typing import Dict, Any
from execution.microstructure.order_book import OrderBook


def compute_microstructure_metrics(
    volume: float,
    adv: float,
    spread_bps: float,
    volatility: float = 0.02
) -> Dict[str, Any]:
    """Calculates microstructure indicators and categorizes liquidity regime."""
    ratio = volume / adv if adv > 0 else 1.0

    if ratio > 1.2 and spread_bps < 5.0:
        liquidity_flag = "HIGH_LIQUIDITY"
    elif ratio > 0.5 and spread_bps < 15.0:
        liquidity_flag = "MEDIUM_LIQUIDITY"
    elif ratio > 0.0:
        liquidity_flag = "LOW_LIQUIDITY"
    else:
        liquidity_flag = "UNKNOWN"

    return {
        "volume_adv_ratio": round(ratio, 4),
        "spread_bps": round(spread_bps, 2),
        "volatility": round(volatility, 4),
        "liquidity_flag": liquidity_flag
    }
