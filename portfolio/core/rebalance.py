"""
Rebalance Event Model for Portfolio Construction OS.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class RebalanceEvent:
    rebalance_id: str
    portfolio_id: str
    timestamp: str
    old_weights: Dict[str, float]
    target_weights: Dict[str, float]
    executed_weights: Dict[str, float]
    turnover: float
    estimated_cost: float
    rebalance_reason: str = "SCHEDULED"
    status: str = "EXECUTED"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
