"""
Central Portfolio Construction Service for Portfolio Construction OS.
"""

from typing import Dict, Any, List, Optional
import os
import json
import hashlib
from datetime import datetime
import numpy as np

from portfolio.core.portfolio import Portfolio, PortfolioSnapshot
from portfolio.core.position import Position
from portfolio.core.rebalance import RebalanceEvent
from portfolio.optimization.equal_weight import EqualWeightOptimizer
from portfolio.optimization.signal_weighted import SignalWeightedOptimizer
from portfolio.optimization.min_variance import MinimumVarianceOptimizer
from portfolio.optimization.mean_variance import MeanVarianceOptimizer
from portfolio.optimization.risk_parity import RiskParityOptimizer
from portfolio.optimization.max_diversification import MaximumDiversificationOptimizer
from portfolio.optimization.constrained import ConstrainedOptimizer
from portfolio.sizing.engine import PositionSizingEngine
from portfolio.constraints.engine import ConstraintEngine
from portfolio.costs.transaction import TransactionCostModel
from portfolio.risk.attribution import PortfolioRiskAttribution
from portfolio.rebalance.engine import RebalanceEngine
from portfolio.utils.covariance import CovarianceEstimator


class PortfolioService:
    """Unified service for Portfolio Construction, Optimization, Risk Attribution, and Rebalancing."""

    def __init__(self, storage_dir: str = "artifacts/portfolio"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.portfolios: Dict[str, Portfolio] = {}

    def create_portfolio(
        self,
        name: str,
        assets: List[str],
        base_currency: str = "USD",
        initial_value: float = 100000.0,
        constraints: Optional[Dict[str, Any]] = None,
        portfolio_id: Optional[str] = None,
    ) -> Portfolio:
        pid = portfolio_id or f"PORT-{len(self.portfolios) + 1:03d}"
        n = len(assets)
        w_eq = 1.0 / n if n > 0 else 0.0

        weights = {a: w_eq for a in assets}
        positions = {}
        for a in assets:
            price = 100.0  # Default initial price
            val = w_eq * initial_value
            qty = val / price if price > 0 else 0.0
            positions[a] = Position(
                symbol=a,
                quantity=qty,
                price=price,
                market_value=val,
                weight=w_eq,
            )

        port = Portfolio(
            portfolio_id=pid,
            name=name,
            base_currency=base_currency,
            assets=assets,
            weights=weights,
            positions=positions,
            constraints=constraints or {},
            total_value=initial_value,
        )
        port.update_exposures()
        self.portfolios[pid] = port
        self._save_portfolio(port)
        return port

    def get_portfolio(self, portfolio_id: str) -> Optional[Portfolio]:
        if portfolio_id in self.portfolios:
            return self.portfolios[portfolio_id]
        filepath = os.path.join(self.storage_dir, f"{portfolio_id}.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
            port = Portfolio.from_dict(data)
            self.portfolios[portfolio_id] = port
            return port
        return None

    def optimize_portfolio(
        self,
        portfolio_id: str,
        method: str = "mean_variance",
        alpha_scores: Optional[Dict[str, float]] = None,
        returns_matrix: Optional[List[List[float]]] = None,
        cov_matrix: Optional[List[List[float]]] = None,
        constraints_override: Optional[Dict[str, Any]] = None,
        asset_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        port = self.get_portfolio(portfolio_id)
        assets = list(alpha_scores.keys()) if alpha_scores else (port.assets if port else ["AAPL", "MSFT", "GOOGL"])

        if not port:
            port = self.create_portfolio(name=f"Portfolio_{portfolio_id}", assets=assets, portfolio_id=portfolio_id)

        # Build covariance matrix if not provided
        if cov_matrix is not None:
            cov = np.array(cov_matrix, dtype=float)
        elif returns_matrix is not None:
            rets = np.array(returns_matrix, dtype=float)
            cov = CovarianceEstimator.sample_covariance(rets)
        else:
            # Synthetic diagonal/sample covariance
            n = len(assets)
            cov = np.eye(n) * 0.04

        merged_constraints = {**port.constraints, **(constraints_override or {})}

        # Select optimizer
        method_lower = method.lower()
        if method_lower == "equal_weight":
            opt = EqualWeightOptimizer({"constraints": merged_constraints})
        elif method_lower == "signal_weighted":
            opt = SignalWeightedOptimizer({"constraints": merged_constraints})
        elif method_lower == "min_variance":
            opt = MinimumVarianceOptimizer({"constraints": merged_constraints, **merged_constraints})
        elif method_lower == "risk_parity":
            opt = RiskParityOptimizer({"constraints": merged_constraints, **merged_constraints})
        elif method_lower == "max_diversification":
            opt = MaximumDiversificationOptimizer({"constraints": merged_constraints, **merged_constraints})
        elif method_lower == "constrained":
            opt = ConstrainedOptimizer({"constraints": merged_constraints, **merged_constraints})
        else:
            opt = MeanVarianceOptimizer({"constraints": merged_constraints, **merged_constraints})

        res = opt.optimize(
            alpha_scores=alpha_scores or {a: 0.01 for a in assets},
            cov_matrix=cov,
            current_weights=port.weights,
            asset_metadata=asset_metadata,
        )

        # Risk Attribution
        risk_attr = PortfolioRiskAttribution.compute_full_attribution(
            weights=res.weights,
            cov_matrix=cov,
            asset_metadata=asset_metadata,
        )

        # Estimate turnover and cost
        cost_model = TransactionCostModel()
        cost_res = cost_model.estimate_cost(
            target_weights=res.weights,
            current_weights=port.weights,
            portfolio_value=port.total_value,
            asset_metadata=asset_metadata,
        )

        # Generate deterministic optimization hash
        config_str = json.dumps({"method": method, "constraints": merged_constraints, "assets": assets}, sort_keys=True)
        opt_hash = hashlib.sha256(config_str.encode("utf-8")).hexdigest()[:16]

        output = {
            "portfolio_id": portfolio_id,
            "optimization_id": f"OPT-{opt_hash}",
            "method": method,
            "target_weights": res.weights,
            "current_weights": port.weights,
            "objective_value": res.objective_value,
            "solver_status": res.solver_status,
            "constraint_status": res.constraint_status,
            "risk_attribution": risk_attr,
            "transaction_costs": cost_res,
            "warnings": res.warnings,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Update portfolio weights
        port.set_weights(res.weights)
        port.optimization_method = method
        self._save_portfolio(port)

        return output

    def rebalance_portfolio(
        self,
        portfolio_id: str,
        target_weights: Dict[str, float],
        timestamp: Optional[str] = None,
        force: bool = False,
    ) -> RebalanceEvent:
        port = self.get_portfolio(portfolio_id)
        if not port:
            port = self.create_portfolio(name=f"Portfolio_{portfolio_id}", assets=list(target_weights.keys()), portfolio_id=portfolio_id)

        ts = timestamp or datetime.utcnow().isoformat() + "Z"
        rebal_engine = RebalanceEngine(port.constraints)

        event = rebal_engine.execute_rebalance(
            portfolio_id=portfolio_id,
            current_weights=port.weights,
            target_weights=target_weights,
            timestamp=ts,
            portfolio_value=port.total_value,
        )

        port.set_weights(target_weights)
        self._save_portfolio(port)
        return event

    def _save_portfolio(self, port: Portfolio) -> None:
        filepath = os.path.join(self.storage_dir, f"{port.portfolio_id}.json")
        with open(filepath, "w") as f:
            json.dump(port.to_dict(), f, indent=2)
