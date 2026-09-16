"""
CLI Script: Promote model lifecycle status (e.g. CANDIDATE -> PAPER champion).
Usage: python models/promote.py --id MODEL-20260916-0001 --status PAPER
"""

from __future__ import annotations
import argparse
import sys
from models.registry.registry import ModelRegistry, ModelStatus


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote Model Status")
    parser.add_argument("--id", type=str, required=True, help="Model ID")
    parser.add_argument("--status", type=str, default="PAPER", help="Target status (CANDIDATE, PAPER)")
    args = parser.parse_args()

    registry = ModelRegistry()
    model = registry.get_model(args.id)
    if not model:
        print(f"Error: Model '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)

    target_st = ModelStatus(args.status.upper())
    success = registry.update_model_status(args.id, target_st)

    if success:
        print(f"Successfully promoted model '{args.id}' to status '{target_st.value}'.")
    else:
        print(f"Failed to promote model '{args.id}'.")


if __name__ == "__main__":
    main()
