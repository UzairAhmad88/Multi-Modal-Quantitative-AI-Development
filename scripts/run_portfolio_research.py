"""
Command-Line Entry Point for Portfolio Optimization & Allocation Experiments.
Usage:
  python scripts/run_portfolio_research.py --config configs/portfolio/mean_variance.yaml --demo
"""

import argparse
import sys
import os
import numpy as np
import pandas as pd

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.portfolio.expected_returns import ExpectedReturnModel
from src.portfolio.covariance import CovarianceEstimator
from src.portfolio.optimizers import (
    EqualWeightOptimizer,
    SignalWeightOptimizer,
    InverseVolatilityOptimizer,
    MinimumVarianceOptimizer,
    MeanVarianceOptimizer,
    RiskParityOptimizer,
    HRPOptimizer,
)
from src.portfolio.risk_budgeting import RiskBudgetEngine
from src.portfolio.position_sizing_advanced import VolatilityTargetingEngine


def main():
    parser = argparse.ArgumentParser(description="Multi-Modal Quant AI - Portfolio Research Runner")
    parser.add_argument("--config", type=str, default="configs/portfolio/mean_variance.yaml", help="Path to portfolio YAML config")
    parser.add_argument("--optimizer", type=str, default="MeanVariance", help="Optimizer name override")
    parser.add_argument("--demo", action="store_true", default=True, help="Run in fast demo mode")
    args = parser.parse_args()

    print("[PORTFOLIO] Starting Quantitative Portfolio Research Experiment...")
    print(f"   Config: {args.config}")
    print(f"   Optimizer Choice: {args.optimizer}")
    print(f"   Demo Mode: {args.demo}")

    symbols = ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL"]
    np.random.seed(42)

    rets = pd.DataFrame(np.random.normal(0.0006, 0.014, (250, len(symbols))), columns=symbols)
    alphas = {s: round(float(np.random.normal(0.02, 0.01)), 4) for s in symbols}

    exp_model = ExpectedReturnModel()
    exp_rets = pd.Series(exp_model.compute_expected_returns(alphas))

    cov_est = CovarianceEstimator(rets)
    cov_df = cov_est.compute_shrinkage_covariance()

    optimizers = {
        "EqualWeight": EqualWeightOptimizer(),
        "SignalWeight": SignalWeightOptimizer(),
        "InverseVolatility": InverseVolatilityOptimizer(),
        "MinimumVariance": MinimumVarianceOptimizer(),
        "MeanVariance": MeanVarianceOptimizer(),
        "RiskParity": RiskParityOptimizer(),
        "HRP": HRPOptimizer(),
    }

    print("\n--- Portfolio Weight Allocations Across Optimizers ---")
    results = []
    for name, opt in optimizers.items():
        w = opt.optimize(exp_rets, cov_df)
        rb_engine = RiskBudgetEngine(cov_df)
        rb_df = rb_engine.compute_risk_contributions(w)
        port_vol = np.sqrt(float((w.values.reshape(-1, 1).T @ cov_df.values @ w.values.reshape(-1, 1)).item()))

        results.append({
            "Optimizer": name,
            "AAPL": round(w.get("AAPL", 0.0), 3),
            "NVDA": round(w.get("NVDA", 0.0), 3),
            "MSFT": round(w.get("MSFT", 0.0), 3),
            "AMZN": round(w.get("AMZN", 0.0), 3),
            "GOOGL": round(w.get("GOOGL", 0.0), 3),
            "Portfolio_Vol_Ann": round(port_vol, 4),
        })

    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))

    # Volatility Targeting Demonstration
    vol_engine = VolatilityTargetingEngine(target_volatility_ann=0.15)
    opt_mv = MeanVarianceOptimizer()
    w_mv = opt_mv.optimize(exp_rets, cov_df)
    scaled_w, mult = vol_engine.scale_portfolio(w_mv, cov_df)
    print(f"\n[VOL TARGET] Scaled portfolio weights for 15% Vol Target (Multiplier: {mult:.2f}x):")
    print(scaled_w.to_dict())

    print("\n[OK] Portfolio Research Experiment Completed Successfully!")


if __name__ == "__main__":
    main()
