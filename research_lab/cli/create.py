"""
CLI tool for creating a new experiment from a template.
"""

import sys
import argparse
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from research_lab.manager import ExperimentManager


def main():
    parser = argparse.ArgumentParser(description="Create Experiment")
    parser.add_argument("--template", type=str, default="multimodal", help="Template name")
    parser.add_argument("--name", type=str, default="New Lab Experiment", help="Experiment name")
    args = parser.parse_args()

    mgr = ExperimentManager()
    exp = mgr.create_experiment(name=args.name, template_name=args.template)

    print(json.dumps({
        "status": "SUCCESS",
        "experiment_id": exp.experiment_id,
        "name": exp.name,
        "template": args.template,
        "configuration_hash": exp.configuration_hash,
        "dataset_id": exp.dataset_id,
        "model_version": exp.model_version
    }, indent=2))


if __name__ == "__main__":
    main()
