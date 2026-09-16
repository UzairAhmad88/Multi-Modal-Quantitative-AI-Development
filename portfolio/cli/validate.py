"""
CLI Tool: Validate Portfolio Constraints.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from portfolio.services.portfolio_service import PortfolioService
from portfolio.constraints.engine import ConstraintEngine


def main():
    parser = argparse.ArgumentParser(description="Validate Portfolio Constraints")
    parser.add_argument("--portfolio", type=str, default="PORT-CLI-001", help="Portfolio ID")
    args = parser.parse_args()

    service = PortfolioService()
    port = service.get_portfolio(args.portfolio)
    if not port:
        port = service.create_portfolio(name="Default CLI Portfolio", assets=["AAPL", "MSFT", "GOOGL"], portfolio_id=args.portfolio)

    engine = ConstraintEngine(port.constraints)
    eval_res = engine.evaluate_all(port.weights, port.weights)

    print(f"Validation Result for Portfolio '{args.portfolio}':")
    print(json.dumps(eval_res, indent=2))


if __name__ == "__main__":
    main()
