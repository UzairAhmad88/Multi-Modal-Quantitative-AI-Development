"""
Risk Snapshot Domain Object for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class RiskSnapshot:
    risk_id: str
    portfolio_id: str
    experiment_id: str = "EXP-001"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    portfolio_value: float = 100000.0
    volatility: float = 0.0
    beta: float = 1.0
    var_95: float = 0.0
    cvar_95: float = 0.0
    maximum_drawdown: float = 0.0
    gross_exposure: float = 1.0
    net_exposure: float = 1.0
    leverage: float = 1.0
    concentration: Dict[str, Any] = field(default_factory=dict)
    risk_contributions: Dict[str, float] = field(default_factory=dict)
    limit_breaches: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    configuration_version: str = "v1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RiskSnapshot":
        return cls(
            risk_id=data["risk_id"],
            portfolio_id=data["portfolio_id"],
            experiment_id=data.get("experiment_id", "EXP-001"),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            portfolio_value=data.get("portfolio_value", 100000.0),
            volatility=data.get("volatility", 0.0),
            beta=data.get("beta", 1.0),
            var_95=data.get("var_95", 0.0),
            cvar_95=data.get("cvar_95", 0.0),
            maximum_drawdown=data.get("maximum_drawdown", 0.0),
            gross_exposure=data.get("gross_exposure", 1.0),
            net_exposure=data.get("net_exposure", 1.0),
            leverage=data.get("leverage", 1.0),
            concentration=data.get("concentration", {}),
            risk_contributions=data.get("risk_contributions", {}),
            limit_breaches=data.get("limit_breaches", []),
            warnings=data.get("warnings", []),
            configuration_version=data.get("configuration_version", "v1.0.0"),
        )
