"""
End-to-End Quantitative Experiment Pipeline CLI
Executes complete pipeline: Data -> Features -> Train -> Validate -> Predict -> Alpha -> Portfolio -> Risk -> Backtest -> Robustness -> Report
Usage:
    python scripts/run_experiment.py --config configs/experiments/multimodal.yaml
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlops.pipelines import FullResearchPipeline


def main():
    parser = argparse.ArgumentParser(description="Run complete quantitative AI research experiment")
    parser.add_argument("--config", type=str, required=True, help="Path to experiment config YAML file")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_file():
        print(f"Error: Config file '{args.config}' not found.")
        sys.exit(1)

    print(f"[MLOps Engine] Executing research pipeline with config: {config_path}")
    pipeline = FullResearchPipeline(config_path=str(config_path))
    results = pipeline.run()

    print("\n" + "=" * 60)
    print("EXPERIMENT EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"Run ID:        {results.get('run_id')}")
    print(f"Status:        {results.get('status')}")
    print(f"Model ID:      {results.get('model_id')}")
    print(f"Backtest Sharpe: {results.get('metrics', {}).get('trading.sharpe_ratio', 'N/A')}")
    print(f"Report path:   {results.get('report_path')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
