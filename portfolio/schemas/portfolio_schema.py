"""
Pydantic Schemas and Dataclasses for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PositionSchema(BaseModel):
    symbol: str = Field(..., description="Asset ticker symbol")
    quantity: float = Field(..., description="Number of shares/units held")
    price: float = Field(..., description="Current asset market price")
    market_value: float = Field(..., description="Total market value of position")
    weight: float = Field(..., description="Portfolio weight [0.0, 1.0]")
    side: str = Field("LONG", description="Position side: LONG or SHORT")
    sector: Optional[str] = Field("Unassigned", description="Sector classification")
    asset_class: Optional[str] = Field("EQUITY", description="Asset class")
    volatility: Optional[float] = Field(0.0, description="Annualized volatility")
    liquidity: Optional[float] = Field(0.0, description="Average Daily Volume (ADV)")


class PortfolioConstraintsSchema(BaseModel):
    long_only: bool = Field(True, description="Strictly non-negative weights")
    max_position_weight: float = Field(0.20, description="Maximum single asset weight")
    min_position_weight: float = Field(0.00, description="Minimum single asset weight")
    sector_limits: Dict[str, float] = Field(default_factory=dict, description="Max exposure per sector")
    asset_class_limits: Dict[str, float] = Field(default_factory=dict, description="Max exposure per asset class")
    max_turnover: float = Field(0.50, description="Max allowed portfolio turnover")
    max_leverage: float = Field(1.00, description="Maximum gross leverage")
    max_cash_weight: float = Field(1.00, description="Maximum cash weight allowed")
    min_cash_weight: float = Field(0.00, description="Minimum cash weight allowed")
    max_adv_participation: float = Field(0.10, description="Max participation rate of ADV")


class OptimizationRequestSchema(BaseModel):
    experiment_id: str = Field("EXP-001", description="Associated experiment ID")
    optimizer_method: str = Field("mean_variance", description="Optimizer method: mean_variance, risk_parity, min_variance, equal_weight, max_diversification, signal_weighted")
    alpha_scores: Dict[str, float] = Field(default_factory=dict, description="Asset alpha predictions")
    covariance_matrix: Optional[List[List[float]]] = Field(None, description="Covariance matrix")
    asset_symbols: List[str] = Field(default_factory=list, description="Asset symbols list")
    current_weights: Optional[Dict[str, float]] = Field(None, description="Current portfolio weights")
    constraints: PortfolioConstraintsSchema = Field(default_factory=PortfolioConstraintsSchema)
    target_volatility: Optional[float] = Field(0.12, description="Target portfolio volatility")
    risk_aversion: float = Field(1.0, description="Risk aversion parameter lambda")
    transaction_cost_bps: float = Field(10.0, description="Transaction cost in basis points")
