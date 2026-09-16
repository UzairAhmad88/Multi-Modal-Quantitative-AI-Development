"""
CLI Script: Train quantitative model from YAML configuration file.
Usage: python models/train.py --config configs/models/multimodal.yaml
"""

from __future__ import annotations
import argparse
import sys
import yaml
from pathlib import Path
from models.training.trainer import ModelTrainingEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Quantitative AI Model")
    parser.add_argument("--config", type=str, required=True, help="Path to model YAML configuration file")
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

    print(f"Initializing model training with config: {config_path}")
    trainer = ModelTrainingEngine()
    result = trainer.train_model(config)

    print("\n--- Model Training Summary ---")
    print(f"Model ID:      {result.get('model_id')}")
    print(f"Name:          {result.get('name')}")
    print(f"Version:       {result.get('version')}")
    print(f"Duration:      {result.get('training_duration_seconds')}s")
    print(f"Artifact Path: {result.get('artifact_path')}")
    print("\nMetrics:")
    for k, v in result.get('metrics', {}).items():
        print(f"  {k:<20}: {v}")


if __name__ == "__main__":
    main()
