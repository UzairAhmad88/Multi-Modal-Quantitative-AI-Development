"""
CLI tool for generating and exporting experiment laboratory report.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research_lab.manager import ExperimentManager


def main():
    parser = argparse.ArgumentParser(description="Export Experiment Report")
    parser.add_argument("--experiment", type=str, default="EXP-001", help="Experiment ID")
    parser.add_argument("--format", type=str, default="markdown", choices=["markdown", "html", "json"], help="Format")
    args = parser.parse_args()

    mgr = ExperimentManager()
    res = mgr.run_experiment(args.experiment)
    reports = res["reports"]

    if args.format == "html":
        print(reports["html"])
    elif args.format == "json":
        print(reports["json"])
    else:
        print(reports["markdown"])


if __name__ == "__main__":
    main()
