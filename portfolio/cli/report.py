"""
CLI Tool: Generate Portfolio Report.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from portfolio.services.portfolio_service import PortfolioService
from portfolio.reports.generator import PortfolioReportGenerator


def main():
    parser = argparse.ArgumentParser(description="Generate Portfolio Report")
    parser.add_argument("--portfolio", type=str, default="PORT-CLI-001", help="Portfolio ID")
    parser.add_argument("--method", type=str, default="mean_variance", help="Optimization method")
    args = parser.parse_args()

    service = PortfolioService()
    opt_res = service.optimize_portfolio(portfolio_id=args.portfolio, method=args.method)
    report_md = PortfolioReportGenerator.generate_report_md(opt_res)

    print(report_md)


if __name__ == "__main__":
    main()
