"""
Model Registry CLI Tool
Allows listing, registering, validating, promoting, and archiving models in Model Registry.
Usage:
    python scripts/models.py list
    python scripts/models.py register --name <NAME> --type <TYPE> --version <VER>
    python scripts/models.py validate --model-id <ID>
    python scripts/models.py promote --model-id <ID> --status <PAPER|VALIDATED>
    python scripts/models.py archive --model-id <ID>
"""

import sys
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.mlops.models import ModelRegistry


def main():
    parser = argparse.ArgumentParser(description="Model Registry CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Model registry commands")

    # list
    subparsers.add_parser("list", help="List registered models")

    # register
    reg_parser = subparsers.add_parser("register", help="Register a new model")
    reg_parser.add_argument("--name", type=str, required=True)
    reg_parser.add_argument("--type", type=str, required=True)
    reg_parser.add_argument("--version", type=str, default="v1.0.0")
    reg_parser.add_argument("--framework", type=str, default="PyTorch")

    # validate
    val_parser = subparsers.add_parser("validate", help="Validate a model")
    val_parser.add_argument("--model-id", type=str, required=True)

    # promote
    prom_parser = subparsers.add_parser("promote", help="Promote a model")
    prom_parser.add_argument("--model-id", type=str, required=True)
    prom_parser.add_argument("--status", type=str, default="PAPER", choices=["VALIDATED", "PAPER", "EXPERIMENTAL"])

    # archive
    arch_parser = subparsers.add_parser("archive", help="Archive a model")
    arch_parser.add_argument("--model-id", type=str, required=True)

    args = parser.parse_args()

    model_reg = ModelRegistry()

    if args.command == "list":
        models = model_reg.list_models()
        print(f"Total Registered Models: {len(models)}")
        for m in models:
            print(f"[{m['model_id']}] {m['model_name']} ({m['version']}) | Type: {m['model_type']} | Status: {m['status']}")

    elif args.command == "register":
        entry = model_reg.register_model(
            model_name=args.name,
            model_type=args.type,
            version=args.version,
            framework=args.framework
        )
        print(f"Registered model successfully: {entry['model_id']}")

    elif args.command == "validate":
        updated = model_reg.update_status(args.model_id, "VALIDATED")
        print(f"Model {args.model_id} status updated to: {updated['status']}")

    elif args.command == "promote":
        updated = model_reg.update_status(args.model_id, args.status)
        print(f"Model {args.model_id} status promoted to: {updated['status']}")

    elif args.command == "archive":
        updated = model_reg.update_status(args.model_id, "ARCHIVED")
        print(f"Model {args.model_id} archived.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
