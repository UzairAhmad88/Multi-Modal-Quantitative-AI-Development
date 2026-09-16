"""
CLI script: List registered quantitative research experiments with filtering.
Usage: python research/list_experiments.py [--model multimodal] [--symbol AAPL] [--status COMPLETED] [--name baseline]
"""

from __future__ import annotations
import argparse
from research.registry.registry import ExperimentRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="List Quantitative Research Experiments")
    parser.add_argument("--model", type=str, default=None, help="Filter by model type (e.g. multimodal, lstm)")
    parser.add_argument("--symbol", type=str, default=None, help="Filter by ticker symbol (e.g. AAPL)")
    parser.add_argument("--status", type=str, default=None, help="Filter by status (e.g. COMPLETED, FAILED)")
    parser.add_argument("--dataset", type=str, default=None, help="Filter by dataset ID or version")
    parser.add_argument("--name", type=str, default=None, help="Filter by experiment name substring")
    args = parser.parse_args()

    registry = ExperimentRegistry()
    results = registry.list_experiments(
        model=args.model,
        symbol=args.symbol,
        status=args.status,
        dataset=args.dataset,
        name=args.name
    )

    print(f"Found {len(results)} experiment runs matching criteria:")
    print("-" * 90)
    print(f"{'Run ID':<20} {'Experiment ID':<20} {'Status':<12} {'Model':<15} {'Timestamp'}")
    print("-" * 90)
    for run in results:
        run_id = run.get("run_id", "N/A")
        exp_id = run.get("experiment_id", "N/A")
        status = run.get("status", "N/A")
        model = run.get("config", {}).get("model", {}).get("type", "N/A")
        ts = run.get("timestamp", "")[:19]
        print(f"{run_id:<20} {exp_id:<20} {status:<12} {model:<15} {ts}")
    print("-" * 90)


if __name__ == "__main__":
    main()
