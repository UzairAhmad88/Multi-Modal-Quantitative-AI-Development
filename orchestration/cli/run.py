"""
CLI for executing the End-to-End Quantitative Research Pipeline.
"""

import argparse
import sys
import yaml
from orchestration.services.orchestration_service import OrchestrationService
from orchestration.reports.generator import ResearchReportGenerator


def main():
    parser = argparse.ArgumentParser(description="Run End-to-End Quantitative Research Pipeline")
    parser.add_argument("--config", type=str, default="orchestration/configs/development.yaml", help="Path to config YAML")
    parser.add_argument("--experiment", type=str, default="EXP-END2END-001", help="Experiment ID")
    parser.add_argument("--save-report", action="store_true", help="Print Markdown research report")
    args = parser.parse_args()

    cfg = {}
    try:
        with open(args.config, "r") as f:
            cfg = yaml.safe_load(f) or {}
    except Exception:
        pass

    service = OrchestrationService()
    run_state = service.run_pipeline(
        experiment_id=args.experiment,
        symbols=cfg.get("experiment", {}).get("symbols", ["AAPL", "MSFT"]),
        config=cfg,
    )

    print(f"=== End-to-End Research Pipeline Execution ===")
    print(f"Run ID: {run_state.run_id}")
    print(f"Status: {run_state.status}")
    print(f"Completed Stages ({len(run_state.completed_stages)}/14): {', '.join(run_state.completed_stages)}")
    print(f"Duration: {run_state.duration_seconds:.2f}s")

    if args.save_report and run_state.status == "COMPLETED":
        # Generate report
        from orchestration.pipeline_context import PipelineContext
        context = PipelineContext(experiment_id=args.experiment, run_id=run_state.run_id)
        generator = ResearchReportGenerator()
        print("\n" + generator.generate_research_report(context))


if __name__ == "__main__":
    main()
