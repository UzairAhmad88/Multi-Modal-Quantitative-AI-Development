"""
Risk Result Models for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class DrawdownEvent:
    start_date: str
    trough_date: str
    recovery_date: Optional[str]
    peak_value: float
    trough_value: float
    drawdown: float
    duration: int  # days to trough
    recovery_duration: Optional[int]  # days from trough to recovery

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StressTestResult:
    scenario_id: str
    portfolio_id: str
    base_value: float
    stressed_value: float
    absolute_loss: float
    percentage_loss: float
    risk_metrics: Dict[str, Any] = field(default_factory=dict)
    constraint_violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RiskResult:
    risk_id: str
    portfolio_id: str
    market_risk: Dict[str, Any]
    portfolio_risk: Dict[str, Any]
    tail_risk: Dict[str, Any]
    drawdown_analysis: Dict[str, Any]
    stress_results: Dict[str, Any] = field(default_factory=dict)
    monte_carlo_results: Dict[str, Any] = field(default_factory=dict)
    risk_limits_status: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
