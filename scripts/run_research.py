"""
Command-Line Entry Point for Quantitative Research Experiments.
Usage:
  python scripts/run_research.py --config configs/research/baseline.yaml --demo
"""

import argparse
import sys
import os

# Add workspace root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.research.runner import ResearchRunner


def main():
    parser = argparse.ArgumentParser(description="Multi-Modal Quant AI - Research Experiment Runner")
    parser.add_argument("--config", type=str, default="configs/research/baseline.yaml", help="Path to YAML research config")
    parser.add_argument("--experiment", type=str, default=None, help="Experiment name override")
    parser.add_argument("--asset", type=str, default=None, help="Asset ticker override")
    parser.add_argument("--demo", action="store_true", default=True, help="Run in fast demo mode")
    args = parser.parse_args()

    print("[RESEARCH] Starting Research Experiment...")
    print(f"   Config: {args.config}")
    print(f"   Demo Mode: {args.demo}")

    runner = ResearchRunner(args.config)
    if args.experiment:
        runner.config["experiment_id"] = args.experiment
    if args.asset:
        runner.config["ticker"] = args.asset

    results = runner.run_experiment(demo=args.demo)

    print("\n[OK] Research Experiment Complete!")
    print(f"   Experiment ID: {results['experiment_id']}")
    print(f"   Mean IC: {results['ic_analysis']['mean_ic']}")
    print(f"   ICIR: {results['ic_analysis']['icir']}")
    print(f"   Sharpe (10 bps fee): {results['cost_sensitivity_sharpe'][2]['sharpe'] if len(results['cost_sensitivity_sharpe'])>2 else 'N/A'}")
    print(f"   Bootstrap Sharpe 95% CI: [{results['bootstrap_confidence_intervals']['sharpe']['ci_lower']}, {results['bootstrap_confidence_intervals']['sharpe']['ci_upper']}]")


if __name__ == "__main__":
    main()
