"""
CLI for running Model Monitoring & Research Health Audit.
"""

import argparse
import sys
from monitoring.services.monitoring_service import MonitoringService
from monitoring.reports.generator import MonitoringReportGenerator


def main():
    parser = argparse.ArgumentParser(description="Run Model Monitoring & Drift Audit")
    parser.add_argument("--experiment", type=str, default="EXP-001", help="Experiment ID")
    parser.add_argument("--save-report", action="store_true", help="Print Markdown report")
    args = parser.parse_args()

    service = MonitoringService()
    result = service.run_monitoring(experiment_id=args.experiment)

    print(f"=== Model Monitoring Audit Complete ===")
    print(f"Monitoring ID: {result.monitoring_id}")
    print(f"Health Score: {result.health_score.overall_health_score:.1f} ({result.health_score.status})")
    print(f"Drifted Features Count: {sum(1 for d in result.data_drift_results if d.is_drifted)}")
    print(f"Alerts Triggered: {len(result.alerts)}")

    if args.save_report:
        generator = MonitoringReportGenerator()
        print("\n" + generator.generate_markdown_report(result))


if __name__ == "__main__":
    main()
