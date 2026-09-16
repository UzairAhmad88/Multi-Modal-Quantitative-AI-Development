"""
CLI Script: Show detailed metadata, configuration, and evaluation metrics for a model ID.
Usage: python models/show.py --id MODEL-20260916-0001
"""

from __future__ import annotations
import argparse
import json
import sys
from models.registry.registry import ModelRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="Show Quantitative Model Details")
    parser.add_argument("--id", type=str, required=True, help="Model ID")
    args = parser.parse_args()

    registry = ModelRegistry()
    model = registry.get_model(args.id)

    if not model:
        print(f"Error: Model ID '{args.id}' not found in registry.", file=sys.stderr)
        sys.exit(1)

    print("=" * 65)
    print(f"MODEL: {model.get('model_id')}")
    print("=" * 65)
    print(f"Name:          {model.get('name')}")
    print(f"Version:       {model.get('version')}")
    print(f"Type:          {model.get('model_type')}")
    print(f"Task:          {model.get('task')}")
    print(f"Status:        {model.get('status')}")
    print(f"Artifact Path: {model.get('artifact_path')}")
    print(f"Created At:    {model.get('created_at')}")
    print("=" * 65)
    print("\nMetrics:")
    print(json.dumps(model.get("metrics", {}), indent=2))
    print("\nConfiguration:")
    print(json.dumps(model.get("config", {}), indent=2))


if __name__ == "__main__":
    main()
