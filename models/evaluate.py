"""
CLI Script: Evaluate quantitative model on test dataset.
Usage: python models/evaluate.py --id MODEL-20260916-0001
"""

from __future__ import annotations
import argparse
import sys
import json
import numpy as np
from models.registry.registry import ModelRegistry
from models.evaluation.evaluator import ModelEvaluator
from models.factory.factory import ModelFactory


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Quantitative Model")
    parser.add_argument("--id", type=str, required=True, help="Model ID to evaluate")
    args = parser.parse_args()

    registry = ModelRegistry()
    model_meta = registry.get_model(args.id)

    if not model_meta:
        print(f"Error: Model ID '{args.id}' not found in registry.", file=sys.stderr)
        sys.exit(1)

    config = model_meta.get("config", {})
    model = ModelFactory.create_model(config, model_id=args.id)

    np.random.seed(42)
    X_test = np.random.normal(0, 1, (50, 16))
    y_test = 0.3 * X_test[:, 0] + np.random.normal(0, 0.05, 50)

    evaluator = ModelEvaluator()
    results = evaluator.evaluate_model(model, X_test, y_test, task=model_meta.get("task", "regression"))

    print("=" * 65)
    print(f"MODEL EVALUATION SUMMARY: {args.id}")
    print("=" * 65)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
