"""
Monte Carlo Risk Engine for Advanced Risk Engine OS.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import os
import json
from risk.monte_carlo.distributions import ReturnDistribution
from risk.tail.var import VaREngine
from risk.tail.cvar import CVaREngine


class MonteCarloRiskEngine:
    """Simulates correlated return paths and calculates Monte Carlo VaR/CVaR distributions."""

    def __init__(self, storage_dir: str = "artifacts/risk/monte_carlo"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def run_simulation(
        self,
        portfolio_id: str,
        weights: Dict[str, float],
        cov_matrix: np.ndarray,
        mean_returns: Optional[np.ndarray] = None,
        num_simulations: int = 10000,
        horizon_days: int = 1,
        random_seed: int = 42,
        base_value: float = 100000.0,
    ) -> Dict[str, Any]:
        assets = list(weights.keys())
        w_vec = np.array([weights[a] for a in assets], dtype=float)
        n = len(assets)

        mu = mean_returns if mean_returns is not None else np.zeros(n)

        sim_asset_returns = ReturnDistribution.generate_correlated_normal(
            mean_returns=mu,
            cov_matrix=cov_matrix,
            num_simulations=num_simulations,
            horizon_days=horizon_days,
            seed=random_seed,
        )

        # Portfolio P&L: PnL = V_base * sum(w_i * r_i)
        sim_port_returns = sim_asset_returns @ w_vec
        sim_pnl = base_value * sim_port_returns

        mc_var_95 = VaREngine.monte_carlo_var(sim_pnl, confidence_level=0.95)
        mc_var_99 = VaREngine.monte_carlo_var(sim_pnl, confidence_level=0.99)
        mc_cvar_95 = float(-np.mean(sim_pnl[sim_pnl <= -mc_var_95])) if np.any(sim_pnl <= -mc_var_95) else mc_var_95

        mean_pnl = float(np.mean(sim_pnl))
        median_pnl = float(np.median(sim_pnl))
        q5 = float(np.percentile(sim_pnl, 5.0))
        q95 = float(np.percentile(sim_pnl, 95.0))

        # Save large raw simulation array to artifact
        sim_id = f"MC-{portfolio_id}-{random_seed}"
        artifact_path = os.path.join(self.storage_dir, f"{sim_id}.npy")
        np.save(artifact_path, sim_pnl)

        return {
            "simulation_id": sim_id,
            "portfolio_id": portfolio_id,
            "simulations": num_simulations,
            "horizon_days": horizon_days,
            "random_seed": random_seed,
            "mc_var_95": float(mc_var_95),
            "mc_var_99": float(mc_var_99),
            "mc_cvar_95": float(mc_cvar_95),
            "mean_pnl": mean_pnl,
            "median_pnl": median_pnl,
            "quantile_5pct": q5,
            "quantile_95pct": q95,
            "artifact_path": artifact_path,
        }
