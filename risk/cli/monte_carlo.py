"""
CLI Tool: Run Monte Carlo Simulation.
"""

import argparse
import json
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from risk.services.risk_service import RiskService


def main():
    parser = argparse.ArgumentParser(description="Run Monte Carlo Risk Simulation")
    parser.add_argument("--portfolio", type=str, default="PORT-CLI-001", help="Portfolio ID")
    parser.add_argument("--simulations", type=int, default=10000, help="Number of paths")
    parser.add_argument("--seed", type=int, default=42, help="Stochastic seed")
    args = parser.parse_args()

    service = RiskService()
    weights = {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.3}
    cov = np.eye(3) * 0.04

    res = service.engine.mc_engine.run_simulation(
        portfolio_id=args.portfolio,
        weights=weights,
        cov_matrix=cov,
        num_simulations=args.simulations,
        random_seed=args.seed,
    )

    print("Monte Carlo Simulation Output:")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
