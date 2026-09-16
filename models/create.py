"""
CLI Script: Instantiate quantitative model using ModelFactory.
Usage: python models/create.py --type lstm (or transformer, multimodal, xgboost)
"""

from __future__ import annotations
import argparse
import sys
from models.factory.factory import ModelFactory


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Model via ModelFactory")
    parser.add_argument("--type", type=str, required=True, help="Model type (lstm, transformer, multimodal, xgboost, random_forest)")
    args = parser.parse_args()

    config = {
        "model": {
            "name": f"factory_{args.type}",
            "type": args.type,
            "version": "1.0.0"
        }
    }

    try:
        model = ModelFactory.create_model(config)
        print("=" * 65)
        print(f"INSTANTIATED MODEL VIA FACTORY: {model.model_id}")
        print("=" * 65)
        print(f"Name:    {model.name}")
        print(f"Version: {model.version}")
        print(f"Type:    {args.type}")
    except Exception as e:
        print(f"Error creating model: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
