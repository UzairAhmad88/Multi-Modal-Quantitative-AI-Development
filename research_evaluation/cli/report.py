"""
CLI tool for generating and exporting Markdown/HTML strategy evaluation reports.
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research_evaluation.manager import ResearchEvaluationManager


def main():
    parser = argparse.ArgumentParser(description="Generate Research Evaluation Report")
    parser.add_argument("--evaluation", type=str, default="EVAL-LATEST", help="Evaluation ID")
    parser.add_argument("--format", type=str, default="markdown", choices=["markdown", "html"], help="Report Format")
    args = parser.parse_args()

    mgr = ResearchEvaluationManager()
    res = mgr.evaluate_strategy()

    if args.format == "html":
        print(res["html_report"])
    else:
        print(res["markdown_report"])


if __name__ == "__main__":
    main()
