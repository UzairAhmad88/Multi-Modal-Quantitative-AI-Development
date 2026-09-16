"""
Research CLI Tool
Allows listing, running, comparing, reproducing, and reporting on quantitative research experiments.
Usage:
    python scripts/research.py list
    python scripts/research.py run --config <CONFIG>
    python scripts/research.py compare --runs <ID1> <ID2>
    python scripts/research.py reproduce --run-id <ID>
    python scripts/research.py report --run-id <ID>
"""

import sys
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlops.experiments import ExperimentManager
from src.mlops.pipelines import FullResearchPipeline
from src.mlops.reproducer import ExperimentReproducer
from src.mlops.metrics_store import MetricStore


def main():
    parser = argparse.ArgumentParser(description="Research CLI Engine")
    subparsers = parser.add_subparsers(dest="command", help="Research commands")

    # list
    subparsers.add_parser("list", help="List all experiments")

    # run
    run_parser = subparsers.add_parser("run", help="Run experiment from config")
    run_parser.add_argument("--config", type=str, required=True, help="Path to config YAML")

    # compare
    comp_parser = subparsers.add_parser("compare", help="Compare research runs")
    comp_parser.add_argument("--runs", nargs="+", required=True, help="Run IDs to compare")

    # reproduce
    repro_parser = subparsers.add_parser("reproduce", help="Reproduce a run")
    repro_parser.add_argument("--run-id", type=str, required=True, help="Run ID to reproduce")

    # report
    report_parser = subparsers.add_parser("report", help="View report for run")
    report_parser.add_argument("--run-id", type=str, required=True, help="Run ID")

    args = parser.parse_args()

    exp_mgr = ExperimentManager()
    metric_st = MetricStore()

    if args.command == "list":
        exps = exp_mgr.list_experiments()
        print(f"Total Experiments: {len(exps)}")
        for e in exps:
            print(f"[{e['experiment_id']}] {e['experiment_name']} | Status: {e['status']} | Created: {e['created_at']}")

    elif args.command == "run":
        pipeline = FullResearchPipeline(config_path=args.config)
        res = pipeline.run()
        print(f"Completed run: {res.get('run_id')}")

    elif args.command == "compare":
        print(f"Comparing runs: {args.runs}")
        comparison = {}
        for rid in args.runs:
            comparison[rid] = metric_st.get_run_metrics(rid)
        print(json.dumps(comparison, indent=2))

    elif args.command == "reproduce":
        reproducer = ExperimentReproducer()
        res = reproducer.reproduce(args.run_id)
        print(json.dumps(res, indent=2))

    elif args.command == "report":
        run_dir = Path("artifacts/runs") / args.run_id / "reports" / "summary.md"
        if run_dir.exists():
            print(run_dir.read_text())
        else:
            print(f"Report for run {args.run_id} not found at {run_dir}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
