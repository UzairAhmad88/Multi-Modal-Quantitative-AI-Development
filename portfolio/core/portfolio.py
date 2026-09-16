"""
Portfolio Domain Object and Snapshot Models for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from portfolio.core.position import Position


@dataclass
class PortfolioSnapshot:
    timestamp: str
    weights: Dict[str, float]
    positions: Dict[str, Dict[str, Any]]
    cash_weight: float
    gross_exposure: float
    net_exposure: float
    portfolio_value: float
    risk_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Portfolio:
    portfolio_id: str
    name: str
    base_currency: str = "USD"
    assets: List[str] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)
    positions: Dict[str, Position] = field(default_factory=dict)
    cash_weight: float = 1.0
    gross_exposure: float = 0.0
    net_exposure: float = 0.0
    leverage: float = 0.0
    constraints: Dict[str, Any] = field(default_factory=dict)
    optimization_method: str = "equal_weight"
    risk_model: str = "sample_covariance"
    total_value: float = 100000.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def update_exposures(self) -> None:
        """Recalculate gross exposure, net exposure, leverage, and cash weight."""
        long_sum = sum(w for w in self.weights.values() if w > 0)
        short_sum = sum(abs(w) for w in self.weights.values() if w < 0)

        self.gross_exposure = long_sum + short_sum
        self.net_exposure = long_sum - short_sum
        self.leverage = self.gross_exposure
        self.cash_weight = max(0.0, 1.0 - self.net_exposure)
        self.updated_at = datetime.utcnow().isoformat() + "Z"

    def set_weights(self, new_weights: Dict[str, float]) -> None:
        """Update weights and recalculate exposures."""
        self.weights = {k: float(v) for k, v in new_weights.items()}
        self.assets = list(self.weights.keys())
        self.update_exposures()

    def create_snapshot(self, timestamp: Optional[str] = None, risk_metrics: Optional[Dict[str, Any]] = None) -> PortfolioSnapshot:
        """Generate point-in-time portfolio snapshot."""
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        pos_dict = {sym: pos.to_dict() for sym, pos in self.positions.items()}
        return PortfolioSnapshot(
            timestamp=timestamp,
            weights=self.weights.copy(),
            positions=pos_dict,
            cash_weight=self.cash_weight,
            gross_exposure=self.gross_exposure,
            net_exposure=self.net_exposure,
            portfolio_value=self.total_value,
            risk_metrics=risk_metrics or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["positions"] = {sym: pos.to_dict() for sym, pos in self.positions.items()}
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Portfolio":
        positions = {}
        if "positions" in data and isinstance(data["positions"], dict):
            for sym, pos_data in data["positions"].items():
                positions[sym] = Position.from_dict(pos_data) if isinstance(pos_data, dict) else pos_data

        port = cls(
            portfolio_id=data["portfolio_id"],
            name=data["name"],
            base_currency=data.get("base_currency", "USD"),
            assets=data.get("assets", []),
            weights=data.get("weights", {}),
            positions=positions,
            cash_weight=data.get("cash_weight", 1.0),
            gross_exposure=data.get("gross_exposure", 0.0),
            net_exposure=data.get("net_exposure", 0.0),
            leverage=data.get("leverage", 0.0),
            constraints=data.get("constraints", {}),
            optimization_method=data.get("optimization_method", "equal_weight"),
            risk_model=data.get("risk_model", "sample_covariance"),
            total_value=data.get("total_value", 100000.0),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat() + "Z"),
        )
        port.update_exposures()
        return port
