"""
CLI Tool: Optimize Portfolio.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from portfolio.services.portfolio_service import PortfolioService
from portfolio.reports.generator import PortfolioReportGenerator


def main():
    parser = argparse.ArgumentParser(description="Run Portfolio Optimization Engine")
    parser.add_argument("--portfolio-id", type=str, default="PORT-CLI-001", help="Portfolio ID")
    parser.add_argument("--method", type=str, default="mean_variance", help="Optimization method")
    parser.add_argument("--risk-aversion", type=float, default=1.0, help="Risk aversion lambda")
    parser.add_argument("--report", action="store_true", help="Generate human markdown report")

    args = parser.parse_args()
    service = PortfolioService()

    print(f"Running Portfolio Optimization using method: {args.method} for portfolio '{args.portfolio_id}'...")

    alpha_scores = {"AAPL": 0.04, "MSFT": 0.03, "GOOGL": 0.02, "AMZN": 0.05, "NVDA": 0.08}
    result = service.optimize_portfolio(
        portfolio_id=args.portfolio_id,
        method=args.method,
        alpha_scores=alpha_scores,
        constraints_override={"risk_aversion": args.risk_aversion},
    )

    if args.report:
        report_md = PortfolioReportGenerator.generate_report_md(result)
        print("\n" + report_md)
    else:
        print("\nOptimization Output:")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
