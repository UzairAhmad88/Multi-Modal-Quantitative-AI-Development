"""
Master Portfolio Optimization Manager for Generating Risk-Aware Constrained Target Portfolios.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import datetime
import json
import hashlib
from pathlib import Path

from portfolio_optimization.estimators.expected_returns import ExpectedReturnEstimator
from portfolio_optimization.estimators.covariance import CovarianceEstimator
from portfolio_optimization.constraints.constraint_engine import ConstraintEngine
from portfolio_optimization.objectives.composite_objective import ObjectiveEngine
from portfolio_optimization.optimizers.allocators import (
    EqualWeightAllocator,
    InverseVolatilityAllocator,
    SignalWeightAllocator,
    RiskParityAllocator,
    MeanVarianceOptimizer,
    MinimumVarianceOptimizer,
    TargetVolatilityOptimizer
)
from portfolio_optimization.position_sizing.position_sizer import PositionSizingEngine
from portfolio_optimization.transaction_costs.cost_engine import TransactionCostEngine
from portfolio_optimization.portfolio.rebalancer import RebalancingEngine
from portfolio_optimization.risk.risk_attribution import RiskAttributionEngine
from portfolio_optimization.attribution.performance_attribution import PerformanceAttributionEngine
from portfolio_optimization.scenarios.scenario_engine import ScenarioEngine


class PortfolioOptimizationManager:
    """Master Orchestrator for Portfolio Construction, Optimization, and Rebalancing."""

    def __init__(self, registry_file: str = "artifacts/portfolio_optimizations.json"):
        self.registry_path = Path(registry_file)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"portfolios": {}}

    def _save(self) -> None:
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def optimize_portfolio(
        self,
        alpha_signals: Dict[str, float],
        returns_df: Optional[pd.DataFrame] = None,
        current_weights: Optional[Dict[str, float]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Runs portfolio optimization workflow given alpha signals and historical returns."""
        config = config or {}
        port_cfg = config.get("portfolio", {})
        method = port_cfg.get("method", "mean_variance")
        name = port_cfg.get("name", "multimodal_portfolio")

        assets = list(alpha_signals.keys()) if alpha_signals else (list(returns_df.columns) if returns_df is not None else [])
        if not assets:
            return {"status": "FAILED", "reason": "No asset signals or return data provided"}

        # 1. Expected Returns & Covariance
        exp_ret_est = ExpectedReturnEstimator.estimate_from_signals(alpha_signals)
        if returns_df is not None and not returns_df.empty:
            cov, cov_assets = CovarianceEstimator.estimate_covariance(returns_df)
        else:
            n = len(assets)
            cov = np.eye(n) * (0.20 ** 2 / 252.0) * 252.0

        # 2. Constraints & Cost Engine
        constraint_engine = ConstraintEngine(config.get("constraints", {}))
        cost_engine = TransactionCostEngine(
            commission_bps=config.get("transaction_costs", {}).get("commission_bps", 1.0),
            slippage_bps=config.get("transaction_costs", {}).get("slippage_bps", 5.0)
        )

        # 3. Method Allocation
        if method == "equal_weight":
            raw_weights = EqualWeightAllocator.allocate(assets)
        elif method == "inverse_volatility":
            raw_weights = InverseVolatilityAllocator.allocate(cov, assets)
        elif method == "signal_weight":
            raw_weights = SignalWeightAllocator.allocate(alpha_signals)
        elif method == "risk_parity":
            raw_weights = RiskParityAllocator.allocate(cov, assets)
        elif method == "minimum_variance":
            raw_weights = MinimumVarianceOptimizer.allocate(cov, assets)
        elif method == "target_volatility":
            base = EqualWeightAllocator.allocate(assets)
            target_vol = config.get("risk", {}).get("target_volatility", 0.15)
            raw_weights = TargetVolatilityOptimizer.allocate(base, cov, assets, target_vol=target_vol)
        else:  # mean_variance
            risk_aversion = config.get("objective", {}).get("risk_aversion", 2.0)
            raw_weights = MeanVarianceOptimizer.allocate(
                exp_ret_est, cov, assets, risk_aversion=risk_aversion, constraint_engine=constraint_engine
            )

        # 4. Project & Validate Constraints
        final_weights = constraint_engine.apply_projection(raw_weights)
        is_valid, constraint_issues = constraint_engine.validate_weights(final_weights, current_weights)

        # 5. Risk Attribution & Costs
        risk_attr = RiskAttributionEngine.calculate_risk_contributions(final_weights, cov)
        cost_breakdown = cost_engine.calculate_trade_cost(final_weights, current_weights or {})

        # 6. ID & Lineage Registration
        ts_str = datetime.datetime.utcnow().strftime("%Y%m%d")
        rand_hex = hashlib.md5(f"{name}_{method}_{len(final_weights)}".encode("utf-8")).hexdigest()[:4].upper()
        portfolio_id = f"PORTFOLIO-{ts_str}-{rand_hex}"

        entry = {
            "portfolio_id": portfolio_id,
            "name": name,
            "method": method,
            "weights": final_weights,
            "is_valid": is_valid,
            "constraint_issues": constraint_issues,
            "expected_volatility": risk_attr["portfolio_volatility"],
            "expected_return": round(float(np.dot([final_weights.get(a, 0.0) for a in assets], [exp_ret_est.get(a, 0.0) for a in assets])), 4),
            "transaction_costs": cost_breakdown,
            "risk_attribution": risk_attr["assets"],
            "created_at": datetime.datetime.utcnow().isoformat(),
            "config": config
        }

        self._data["portfolios"][portfolio_id] = entry
        self._save()

        return {
            "status": "OPTIMAL" if is_valid else "FEASIBLE",
            "portfolio_id": portfolio_id,
            "entry": entry
        }

    def list_portfolios(self) -> List[Dict[str, Any]]:
        return list(self._data["portfolios"].values())

    def get_portfolio(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        return self._data["portfolios"].get(portfolio_id)
