"""
CLI Tool: Portfolio Risk Attribution.
"""

import argparse
import json
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from portfolio.services.portfolio_service import PortfolioService
from portfolio.risk.attribution import PortfolioRiskAttribution


def main():
    parser = argparse.ArgumentParser(description="Compute Portfolio Risk Attribution")
    parser.add_argument("--portfolio", type=str, default="PORT-CLI-001", help="Portfolio ID")
    args = parser.parse_args()

    service = PortfolioService()
    port = service.get_portfolio(args.portfolio)
    if not port:
        port = service.create_portfolio(name="Default CLI Portfolio", assets=["AAPL", "MSFT", "GOOGL"], portfolio_id=args.portfolio)

    n = len(port.assets)
    cov = np.eye(n) * 0.04
    attr = PortfolioRiskAttribution.compute_full_attribution(port.weights, cov)

    print(f"Risk Attribution for Portfolio '{args.portfolio}':")
    print(json.dumps(attr, indent=2))


if __name__ == "__main__":
    main()
