"""
CLI Script: Rollback active paper champion model to previous candidate.
Usage: python models/rollback.py --model MODEL-20260916-0001
"""

from __future__ import annotations
import argparse
import sys
from models.lifecycle.rollback import ModelRollbackManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Rollback Active Champion Model")
    parser.add_argument("--model", type=str, default=None, help="Optional model ID to rollback from")
    args = parser.parse_args()

    rollback_mgr = ModelRollbackManager()
    res = rollback_mgr.rollback()

    if res.get("status") == "SUCCESS":
        print(f"Successfully rolled back champion model to '{res['restored_champion']}' (version {res['version']}).")
    else:
        print(f"Rollback failed: {res.get('reason')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
