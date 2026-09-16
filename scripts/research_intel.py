"""
CLI Tool for Research Intelligence (Phase 11).
Usage:
    python scripts/research_intel.py hypothesis create --title "..." --dataset "..."
    python scripts/research_intel.py experiment create --name "..." --hypo-id "..."
    python scripts/research_intel.py experiment list
    python scripts/research_intel.py experiment run --id EXP-2026-000001
    python scripts/research_intel.py experiment compare --ids EXP-2026-000001 EXP-2026-000002
    python scripts/research_intel.py experiment reproduce --id EXP-2026-000001
    python scripts/research_intel.py ablation --experiment-id EXP-2026-000001
    python scripts/research_intel.py robustness --experiment-id EXP-2026-000001
    python scripts/research_intel.py analyze --experiment-id EXP-2026-000001
    python scripts/research_intel.py report --experiment-id EXP-2026-000001
"""

import sys
from pathlib import Path
import argparse
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research_intelligence.orchestration.pipeline import ResearchIntelligencePipeline
from research_intelligence.experiment_manager.manager import ExperimentConfig, ExperimentPriority
from research_intelligence.comparison.comparator import ExperimentComparator

_pipeline = ResearchIntelligencePipeline()


def main():
    parser = argparse.ArgumentParser(description="Multi-Modal Quant AI - Research Intelligence CLI")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Hypothesis Parser
    hypo_parser = subparsers.add_parser("hypothesis", help="Hypothesis management")
    hypo_sub = hypo_parser.add_subparsers(dest="hypo_action")
    hypo_create = hypo_sub.add_parser("create")
    hypo_create.add_argument("--title", required=True)
    hypo_create.add_argument("--description", default="")
    hypo_create.add_argument("--dataset", default="market_sp500")

    # Experiment Parser
    exp_parser = subparsers.add_parser("experiment", help="Experiment management")
    exp_sub = exp_parser.add_subparsers(dest="exp_action")
    
    exp_create = exp_sub.add_parser("create")
    exp_create.add_argument("--name", required=True)
    exp_create.add_argument("--hypo-id", required=True)
    exp_create.add_argument("--model", default="LSTM")
    exp_create.add_argument("--dataset", default="market_sp500")

    exp_list = exp_sub.add_parser("list")

    exp_run = exp_sub.add_parser("run")
    exp_run.add_argument("--id", required=True)
    exp_run.add_argument("--force", action="store_true")

    exp_comp = exp_sub.add_parser("compare")
    exp_comp.add_argument("--ids", nargs=2, required=True)

    exp_repro = exp_sub.add_parser("reproduce")
    exp_repro.add_argument("--id", required=True)

    # Ablation Parser
    ab_parser = subparsers.add_parser("ablation", help="Run feature ablation study")
    ab_parser.add_argument("--experiment-id", required=True)

    # Robustness Parser
    rob_parser = subparsers.add_parser("robustness", help="Run robustness stress test")
    rob_parser.add_argument("--experiment-id", required=True)

    # Analyze Parser
    anz_parser = subparsers.add_parser("analyze", help="Run error diagnostics analysis")
    anz_parser.add_argument("--experiment-id", required=True)

    # Report Parser
    rep_parser = subparsers.add_parser("report", help="Generate Markdown research report")
    rep_parser.add_argument("--experiment-id", required=True)

    args = parser.parse_args()

    if args.command == "hypothesis" and args.hypo_action == "create":
        h = _pipeline.hypothesis_registry.register(
            title=args.title,
            description=args.description,
            research_question=args.title,
            expected_effect="Positive alpha correlation",
            null_hypothesis="Zero correlation",
            variables=["return", "sentiment"],
            dataset=args.dataset,
            time_period="2021-2026",
        )
        print(json.dumps(h.to_dict(), indent=2))

    elif args.command == "experiment":
        if args.exp_action == "create":
            cfg = ExperimentConfig(
                name=args.name,
                hypothesis_id=args.hypo_id,
                dataset=args.dataset,
                features=["market_return", "news_sentiment", "pe_ratio"],
                model=args.model,
            )
            rec = _pipeline.experiment_manager.create_experiment(cfg, auto_approve=True)
            print(json.dumps(rec.to_dict(), indent=2))
        elif args.exp_action == "list":
            exps = [e.to_dict() for e in _pipeline.experiment_manager.list_all()]
            print(json.dumps(exps, indent=2))
        elif args.exp_action == "run":
            record = _pipeline.experiment_manager.get(args.id)
            if not record:
                print(f"Error: Experiment {args.id} not found.")
                return
            _pipeline.experiment_manager.approve_experiment(args.id)
            res = _pipeline.experiment_runner.run_experiment(args.id, force_rerun=args.force)
            print(json.dumps(res, indent=2))
        elif args.exp_action == "compare":
            id1, id2 = args.ids
            e1 = _pipeline.experiment_manager.get(id1)
            e2 = _pipeline.experiment_manager.get(id2)
            if not e1 or not e2:
                print("Error: Experiment ID(s) not found.")
                return
            comp = ExperimentComparator.compare(e1, e2)
            print(json.dumps(comp, indent=2))
        elif args.exp_action == "reproduce":
            record = _pipeline.experiment_manager.get(args.id)
            if not record:
                print(f"Error: Experiment {args.id} not found for reproduction.")
                return
            _pipeline.experiment_manager.approve_experiment(args.id)
            res = _pipeline.experiment_runner.run_experiment(args.id, force_rerun=True)
            print(f"Reproduced Experiment {args.id} successfully:")
            print(json.dumps(res, indent=2))

    elif args.command == "ablation":
        record = _pipeline.experiment_manager.get(args.experiment_id)
        if not record:
            print(f"Error: Experiment {args.experiment_id} not found.")
            return
        res = _pipeline.ablation_engine.run_ablation_study(record.config, record.config.hypothesis_id)
        print(json.dumps(res, indent=2))

    elif args.command == "robustness":
        record = _pipeline.experiment_manager.get(args.experiment_id)
        if not record:
            print(f"Error: Experiment {args.experiment_id} not found.")
            return
        res = _pipeline.robustness_engine.run_robustness_suite(record.config, record.config.hypothesis_id)
        print(json.dumps(res, indent=2))

    elif args.command == "analyze":
        record = _pipeline.experiment_manager.get(args.experiment_id)
        if not record:
            print(f"Error: Experiment {args.experiment_id} not found.")
            return
        res = _pipeline.error_analyzer.analyze_experiment_errors(args.experiment_id, record.config.features)
        print(json.dumps(res, indent=2))

    elif args.command == "report":
        record = _pipeline.experiment_manager.get(args.experiment_id)
        if not record:
            print(f"Error: Experiment {args.experiment_id} not found.")
            return
        path = _pipeline.report_generator.generate_experiment_report(record)
        print(f"Report generated successfully at: {path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
