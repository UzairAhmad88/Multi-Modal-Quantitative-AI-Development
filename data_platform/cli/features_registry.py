"""
CLI for Feature Registry Catalog.
Usage: python data_platform/cli/features_registry.py --list
       python data_platform/cli/features_registry.py --show RSI_14
"""

import argparse
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data_platform.feature_store.registry import FeatureStoreRegistry


def main():
    parser = argparse.ArgumentParser(description="Feature Store Registry Catalog CLI.")
    parser.add_argument("--list", action="store_true", help="List all registered features")
    parser.add_argument("--show", type=str, help="Show details for feature ID")

    args = parser.parse_args()
    reg = FeatureStoreRegistry()

    if args.show:
        feat = reg.get_feature(args.show)
        if feat:
            print(f"[FEATURE DETAILS] {json.dumps(feat, indent=2)}")
        else:
            print(f"[ERROR] Feature '{args.show}' not found.")
    else:
        feats = reg.list_features()
        print(f"[FEATURE STORE CATALOG] Total Features: {len(feats)}")
        for f in feats:
            print(f" - {f['id']} (v{f['version']}): {f['name']} [{f['category']}]")


if __name__ == "__main__":
    main()
