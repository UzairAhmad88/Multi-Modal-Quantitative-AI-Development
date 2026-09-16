"""
CLI Script: List registered quantitative models.
Usage: python models/list.py [--status CANDIDATE] [--type multimodal]
"""

from __future__ import annotations
import argparse
from models.registry.registry import ModelRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="List Registered Quantitative Models")
    parser.add_argument("--status", type=str, default=None, help="Filter by model status (DEVELOPMENT, CANDIDATE, PAPER, etc.)")
    parser.add_argument("--type", type=str, default=None, help="Filter by model type (multimodal, lstm, etc.)")
    args = parser.parse_args()

    registry = ModelRegistry()
    models = registry.list_models(status=args.status, model_type=args.type)
    champion = registry.get_champion()
    champ_id = champion.get("model_id") if champion else "NONE"

    print("=" * 85)
    print(f"REGISTERED QUANTITATIVE MODELS (Active Champion: {champ_id})")
    print("=" * 85)
    print(f"{'Model ID':<22} {'Version':<10} {'Name':<22} {'Status':<14} {'Type'}")
    print("-" * 85)
    for m in models:
        m_id = m.get("model_id", "N/A")
        ver = m.get("version", "N/A")
        name = m.get("name", "N/A")[:20]
        status = m.get("status", "N/A")
        m_type = m.get("model_type", "N/A")
        is_c = " [CHAMPION]" if m_id == champ_id else ""
        print(f"{m_id:<22} {ver:<10} {name:<22} {status:<14} {m_type}{is_c}")
    print("-" * 85)


if __name__ == "__main__":
    main()
