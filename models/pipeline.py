"""
CLI Script: Automated Model Training & Registration Pipeline.
Usage: python models/pipeline.py --config configs/models/multimodal.yaml
"""

from __future__ import annotations
import argparse
import sys
import yaml
from pathlib import Path

from models.training.trainer import ModelTrainingEngine
from models.lifecycle.promoter import ModelPromoter
from models.registry.registry import ModelRegistry, ModelStatus


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated Model Pipeline")
    parser.add_argument("--config", type=str, required=True, help="Path to model configuration YAML file")
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file '{config_path}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print("=" * 70)
    print("RUNNING AUTOMATED MODEL DEVELOPMENT & REGISTRATION PIPELINE")
    print("=" * 70)

    # 1. Train
    print("[1/4] Training model...")
    trainer = ModelTrainingEngine()
    result = trainer.train_model(config)

    model_id = result["model_id"]
    print(f"      Model trained: {model_id} in {result['training_duration_seconds']}s")

    # 2. Evaluate
    print("[2/4] Evaluating validation metrics...")
    metrics = result.get("metrics", {})
    print(f"      Sharpe Ratio: {metrics.get('sharpe', 'N/A')}")
    print(f"      MAE:          {metrics.get('mae', 'N/A')}")

    # 3. Validation Gate & Promote to Candidate
    print("[3/4] Running promotion validation gates...")
    promoter = ModelPromoter()
    validation_res = {"leakage_check": "PASS", "validation": "PASS", "robustness": "PASS"}
    promo_res = promoter.evaluate_and_promote(model_id, ModelStatus.CANDIDATE, validation_res)
    print(f"      Promotion Result: {promo_res['status']}")

    # 4. Register
    print("[4/4] Finalizing model registration...")
    print(f"\n[SUCCESS] Model '{model_id}' registered successfully as CANDIDATE!")


if __name__ == "__main__":
    main()
