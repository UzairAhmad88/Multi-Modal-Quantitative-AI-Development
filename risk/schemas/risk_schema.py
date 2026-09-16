"""
Pydantic Schemas for Advanced Risk & Stress Testing Engine OS.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class RiskLimitSchema(BaseModel):
    max_volatility: float = Field(0.25, description="Max allowed annual portfolio volatility")
    max_var_95: float = Field(0.05, description="Max 95% Value at Risk limit")
    max_cvar_95: float = Field(0.08, description="Max 95% Conditional VaR limit")
    max_drawdown: float = Field(0.20, description="Maximum drawdown threshold")
    max_leverage: float = Field(1.50, description="Gross leverage limit")
    max_hhi: float = Field(0.35, description="Max Herfindahl concentration index")


class StressScenarioRequest(BaseModel):
    scenario_id: str = Field("MARKET_CRASH_20PCT", description="Scenario identifier")
    scenario_type: str = Field("hypothetical", description="Scenario type: historical, hypothetical, shock")
    equity_market_shock: float = Field(-0.20, description="Equity market shock percentage")
    volatility_multiplier: float = Field(1.5, description="Volatility scaling multiplier")
    correlation_warp: float = Field(0.5, description="Correlation matrix warping factor")
    liquidity_spread_multiplier: float = Field(2.0, description="Bid-ask spread multiplier")
    transaction_cost_multiplier: float = Field(2.0, description="Transaction cost multiplier")
    asset_shocks: Dict[str, float] = Field(default_factory=dict, description="Asset-specific price shocks")
    sector_shocks: Dict[str, float] = Field(default_factory=dict, description="Sector-specific price shocks")


class MonteCarloRequest(BaseModel):
    simulations: int = Field(10000, description="Number of Monte Carlo paths")
    horizon: int = Field(1, description="Simulation horizon in days")
    random_seed: int = Field(42, description="Stochastic random seed")
    distribution: str = Field("correlated_normal", description="Return distribution: correlated_normal, historical_empirical")
