"""
CLI script: Compare metrics of two quantitative research experiments or runs.
Usage: python research/compare.py RUN-20260916-0001 RUN-20260916-0002
"""

from __future__ import annotations
import argparse
import sys
from research.registry.registry import ExperimentRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Quantitative Research Runs")
    parser.add_argument("id1", type=str, help="First Run or Experiment ID")
    parser.add_argument("id2", type=str, help="Second Run or Experiment ID")
    args = parser.parse_args()

    registry = ExperimentRegistry()
    res = registry.compare_runs(args.id1, args.id2)

    if "error" in res:
        print(f"Error: {res['error']}", file=sys.stderr)
        sys.exit(1)

    r1_name = res["run_1"]["name"] or res["run_1"]["id"]
    r2_name = res["run_2"]["name"] or res["run_2"]["id"]

    print("=" * 70)
    print(f"COMPARISON: {res['run_1']['id']} vs {res['run_2']['id']}")
    print("=" * 70)
    print(f"{'Metric':<25} {r1_name[:20]:<20} {r2_name[:20]:<20}")
    print("-" * 70)

    metrics = res.get("metrics", {})
    for metric, vals in metrics.items():
        v1 = vals.get("run_1", "N/A")
        v2 = vals.get("run_2", "N/A")
        if isinstance(v1, float):
            v1_str = f"{v1:.4f}"
        else:
            v1_str = str(v1)
        if isinstance(v2, float):
            v2_str = f"{v2:.4f}"
        else:
            v2_str = str(v2)
        print(f"{metric:<25} {v1_str:<20} {v2_str:<20}")

    print("-" * 70)
    print("Note: Quantitative metrics are compared independently without universal scoring.")


if __name__ == "__main__":
    main()
