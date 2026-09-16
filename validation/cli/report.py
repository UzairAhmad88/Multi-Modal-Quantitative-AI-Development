"""
CLI Tool: Inspect Significance & Stability & Report.
"""

import argparse
import json
from validation.core.validation_manager import StatisticalValidationManager
from validation.reports.validation_report_generator import ValidationReportGenerator


def main_significance():
    parser = argparse.ArgumentParser(description="Inspect Significance Results")
    parser.add_argument("--validation", type=str, required=True, help="Validation ID")
    args = parser.parse_args()
    mgr = StatisticalValidationManager()
    val = mgr.get_validation(args.validation)
    if val:
        print(json.dumps([s.model_dump() for s in val.significance_results], indent=2))


def main_stability():
    parser = argparse.ArgumentParser(description="Inspect Stability Results")
    parser.add_argument("--validation", type=str, required=True, help="Validation ID")
    args = parser.parse_args()
    mgr = StatisticalValidationManager()
    val = mgr.get_validation(args.validation)
    if val and val.stability_result:
        print(json.dumps(val.stability_result.model_dump(), indent=2))


def main_report():
    parser = argparse.ArgumentParser(description="Generate Validation Report")
    parser.add_argument("--validation", type=str, required=True, help="Validation ID")
    args = parser.parse_args()
    mgr = StatisticalValidationManager()
    val = mgr.get_validation(args.validation)
    if val:
        md = ValidationReportGenerator.generate_report_md(val)
        print(md)


if __name__ == "__main__":
    main_report()
