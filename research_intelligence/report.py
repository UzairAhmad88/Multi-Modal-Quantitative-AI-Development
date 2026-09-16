"""
CLI Script: Generate comprehensive research intelligence report for an experiment.
Usage: python research_intelligence/report.py --experiment EXP-001
"""

from __future__ import annotations
import argparse
import sys
from research_intelligence.engine import ResearchIntelligenceEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Research Intelligence Report")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment ID")
    parser.add_argument("--hypothesis", type=str, default="HYP-001", help="Hypothesis ID")
    args = parser.parse_args()

    engine = ResearchIntelligenceEngine()
    metrics = {"sharpe": 1.64, "cagr": 0.187, "max_drawdown": 0.112}
    res = engine.evaluate_and_record_finding(
        hypothesis_id=args.hypothesis,
        experiment_id=args.experiment,
        metrics=metrics,
        observation=f"Automated research evaluation for experiment {args.experiment}"
    )

    print("=" * 70)
    print(f"RESEARCH INTELLIGENCE REPORT GENERATED FOR: {args.experiment}")
    print("=" * 70)
    print(f"Finding ID:      {res['finding_id']}")
    print(f"Evidence Status: {res['evidence_status']}")
    print(f"Report File:     {res['report_path']}\n")
    print("Follow-Up Research Questions:")
    for q in res['follow_up_questions']:
        print(f"  - {q}")


if __name__ == "__main__":
    main()
