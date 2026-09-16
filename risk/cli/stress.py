"""
CLI Tool: Run Stress Test Scenarios.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from risk.services.risk_service import RiskService


def main():
    parser = argparse.ArgumentParser(description="Run Stress Testing Scenarios")
    parser.add_argument("--portfolio", type=str, default="PORT-CLI-001", help="Portfolio ID")
    parser.add_argument("--scenario", type=str, default="MARKET_CRASH_20PCT", help="Scenario ID")
    args = parser.parse_args()

    service = RiskService()
    weights = {"AAPL": 0.4, "MSFT": 0.3, "GOOGL": 0.3}

    res = service.engine.stress_engine.run_scenario(
        scenario_id=args.scenario,
        portfolio_id=args.portfolio,
        weights=weights,
    )

    print(f"Stress Test Result for '{args.scenario}':")
    print(json.dumps(res.to_dict(), indent=2))


if __name__ == "__main__":
    main()
