"""
CLI script: Run quantitative research experiment pipeline.
Usage: python research/run_experiment.py --config configs/experiments/example.yaml [--resume RUN-xxxx]
"""

from __future__ import annotations
import argparse
import sys
import yaml
from pathlib import Path
from orchestration.pipeline import ResearchPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Automated Research Pipeline")
    parser.add_argument("--config", type=str, required=True, help="Path to experiment YAML configuration file")
    parser.add_argument("--resume", type=str, default=None, help="Run ID to resume from latest valid checkpoint")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Configuration file not found at '{config_path}'", file=sys.stderr)
        sys.exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML config: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Initializing pipeline with config: {config_path}")
    pipeline = ResearchPipeline(config=config, resume_run_id=args.resume)
    run_record = pipeline.execute()

    print("\n--- Pipeline Execution Summary ---")
    print(f"Experiment ID: {run_record.get('experiment_id')}")
    print(f"Run ID:        {run_record.get('run_id')}")
    print(f"Status:        {run_record.get('status')}")
    print(f"Completed:     {run_record.get('completed_stages')}/{run_record.get('total_stages')} stages")
    
    metrics = run_record.get('metrics', {})
    if metrics:
        print("\nBacktest Metrics:")
        print(f"  Sharpe Ratio:  {metrics.get('sharpe', 'N/A')}")
        print(f"  CAGR:          {metrics.get('cagr', 'N/A')}")
        print(f"  Max Drawdown:  {metrics.get('max_drawdown', 'N/A')}")

    if run_record.get('status') == 'COMPLETED':
        print(f"\nManifest saved: artifacts/experiments/{run_record.get('experiment_id')}/manifest.json")
    else:
        print(f"\nPipeline stopped with status: {run_record.get('status')}")
        if run_record.get('error'):
            print(f"Error details: {run_record.get('error')}")


if __name__ == "__main__":
    main()
