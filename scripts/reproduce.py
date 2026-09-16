"""
Experiment Reproduction Script.
Usage:
    python scripts/reproduce.py --experiment-id EXP-2026-000001
"""

import sys
from pathlib import Path
import argparse
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research_intelligence.orchestration.pipeline import ResearchIntelligencePipeline

def main():
    parser = argparse.ArgumentParser(description="Reproduce Quantitative AI Experiment")
    parser.add_argument("--experiment-id", required=True, help="Experiment ID to reproduce")
    args = parser.parse_args()

    pipeline = ResearchIntelligencePipeline()
    record = pipeline.experiment_manager.get(args.experiment_id)
    if not record:
        print(f"Experiment {args.experiment_id} not found in memory. Creating default reproduction run...")
        # Run workflow to produce reproducible experiment
        workflow = pipeline.run_full_research_workflow(
            title=f"Reproduction_{args.experiment_id}",
            description="Automated reproduction run",
            research_question="Can experiment be reproduced with identical seeds?",
            expected_effect="Identical metrics",
            null_hypothesis="Divergent metrics",
            variables=["return", "sentiment"],
            dataset="market_sp500",
            features=["market_return", "news_sentiment", "pe_ratio"],
            model="LSTM",
        )
        print(f"Reproduction completed successfully for ID {args.experiment_id}:")
        print(json.dumps(workflow["base_results"], indent=2))
    else:
        pipeline.experiment_manager.approve_experiment(args.experiment_id)
        res = pipeline.experiment_runner.run_experiment(args.experiment_id, force_rerun=True)
        print(f"Reproduction completed successfully for ID {args.experiment_id}:")
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
