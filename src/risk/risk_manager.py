from __future__ import annotations
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from src.risk.drawdown import max_drawdown
from src.risk.var import historical_var
from src.risk.volatility import annualized_volatility
from src.risk.exposure import gross_exposure
from src.utils.logger import get_logger

logger = get_logger("risk_manager")


class RiskEngine:
    """Enforces risk constraints (max position, sector limits, max drawdown) and computes risk metrics."""

    def __init__(
        self,
        max_position: float = 0.25,
        max_sector_exposure: float = 0.40,
        max_leverage: float = 1.0,
        max_drawdown_limit: float = 0.20
    ):
        self.max_position = max_position
        self.max_sector_exposure = max_sector_exposure
        self.max_leverage = max_leverage
        self.max_drawdown_limit = max_drawdown_limit

    def validate_and_gate_portfolio(
        self,
        proposed_weights: pd.Series,
        sector_map: Dict[str, str] | None = None,
        current_drawdown: float = 0.0
    ) -> Tuple[pd.Series, Dict[str, Any]]:
        """RISK GATE: Intercepts proposed weights, checks limits, and scales or clips weights if limits fail."""
        weights = proposed_weights.copy()
        violations = []

        # 1. Max Position Gate
        over_pos = weights[weights.abs() > self.max_position]
        if not over_pos.empty:
            violations.append(f"Position limits exceeded for: {list(over_pos.index)}")
            weights = weights.clip(-self.max_position, self.max_position)

        # 2. Sector Exposure Gate
        if sector_map:
            sector_totals: Dict[str, float] = {}
            for ticker, w in weights.items():
                sec = sector_map.get(ticker, "Unknown")
                sector_totals[sec] = sector_totals.get(sec, 0.0) + abs(w)

            for sec, tot in sector_totals.items():
                if tot > self.max_sector_exposure:
                    violations.append(f"Sector '{sec}' exposure ({tot:.2f}) exceeded max ({self.max_sector_exposure:.2f})")
                    # Scale down sector weights
                    scale = self.max_sector_exposure / tot
                    for ticker in weights.index:
                        if sector_map.get(ticker) == sec:
                            weights[ticker] *= scale

        # 3. Max Leverage / Gross Exposure Gate
        gross = gross_exposure(weights)
        if gross > self.max_leverage:
            violations.append(f"Gross exposure ({gross:.2f}) exceeded max leverage ({self.max_leverage:.2f})")
            weights = weights / gross

        # 4. Max Drawdown Circuit Breaker Gate
        if current_drawdown < -self.max_drawdown_limit:
            violations.append(f"Max drawdown breaker triggered ({current_drawdown:.2%}). Scaling to cash.")
            weights = weights * 0.5  # Reduce portfolio risk exposure by 50%

        status = "PASSED" if not violations else "MODIFIED_BY_RISK_GATE"
        risk_report = {
            "status": status,
            "violations": violations,
            "gross_exposure": round(gross_exposure(weights), 4),
            "max_position_actual": round(float(weights.abs().max()) if not weights.empty else 0.0, 4)
        }

        return weights, risk_report

    def compute_portfolio_risk(self, returns_series: pd.Series, equity_series: pd.Series) -> Dict[str, float]:
        """Compute full suite of portfolio risk metrics."""
        vol = annualized_volatility(returns_series)
        mdd = max_drawdown(equity_series)
        var_95 = historical_var(returns_series, confidence=0.95)

        # Expected Shortfall (CVaR 95%)
        cutoff = returns_series.quantile(0.05)
        cvar_95 = float(-returns_series[returns_series <= cutoff].mean()) if not returns_series.empty else 0.0

        return {
            "volatility": round(vol, 4),
            "max_drawdown": round(mdd, 4),
            "var_95": round(var_95, 4),
            "cvar_95": round(cvar_95, 4)
        }


def enforce_max_position(weights: pd.Series, maximum: float = 0.25) -> pd.Series:
    engine = RiskEngine(max_position=maximum)
    gated, _ = engine.validate_and_gate_portfolio(weights)
    return gated
