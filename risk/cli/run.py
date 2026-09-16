"""
CLI Tool: Run Risk Analysis.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from risk.services.risk_service import RiskService
from risk.reports.generator import RiskReportGenerator


def main():
    parser = argparse.ArgumentParser(description="Run Advanced Quantitative Risk Engine Analysis")
    parser.add_argument("--portfolio", type=str, default="PORT-CLI-001", help="Portfolio ID")
    parser.add_argument("--report", action="store_true", help="Generate human markdown report")

    args = parser.parse_args()
    service = RiskService()

    print(f"Executing Risk Analysis for portfolio '{args.portfolio}'...")
    res = service.run_risk_analysis(portfolio_id=args.portfolio)

    if args.report:
        report_md = RiskReportGenerator.generate_report_md(res)
        print("\n" + report_md)
    else:
        print("\nRisk Analysis Output:")
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
