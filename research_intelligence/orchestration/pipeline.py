"""
Research Intelligence End-to-End Orchestration Pipeline.
Connects Hypothesis Management, Experiment Generation, Execution, Comparison, Ablation,
Robustness, Error Diagnostics, Memory, Recommendation, and Reporting into a unified workflow.
"""

from typing import Dict, List, Any, Optional
from research_intelligence.hypothesis.registry import HypothesisRegistry, PreRegistrationSpec, HypothesisState
from research_intelligence.experiment_manager.manager import IntelExperimentManager, ExperimentConfig, ExperimentPriority
from research_intelligence.experiment_runner.runner import IntelExperimentRunner
from research_intelligence.ablation.intel_ablation import IntelAblationEngine
from research_intelligence.robustness.intel_robustness import IntelRobustnessEngine
from research_intelligence.diagnostics.error_analyzer import ErrorAnalyzer
from research_intelligence.research_memory.memory import ResearchMemory
from research_intelligence.recommendation_engine.recommender import ResearchRecommendationEngine
from research_intelligence.report_generator.generator import ResearchReportGenerator


class ResearchIntelligencePipeline:
    """Unified master pipeline for Research Intelligence (Phase 11)."""

    def __init__(self, output_report_dir: str = "reports/research"):
        self.hypothesis_registry = HypothesisRegistry()
        self.experiment_manager = IntelExperimentManager()
        self.research_memory = ResearchMemory()
        self.experiment_runner = IntelExperimentRunner(self.experiment_manager, self.research_memory)
        self.ablation_engine = IntelAblationEngine(self.experiment_manager, self.experiment_runner)
        self.robustness_engine = IntelRobustnessEngine(self.experiment_manager, self.experiment_runner)
        self.error_analyzer = ErrorAnalyzer()
        self.recommendation_engine = ResearchRecommendationEngine()
        self.report_generator = ResearchReportGenerator(output_report_dir)

    def run_full_research_workflow(
        self,
        title: str,
        description: str,
        research_question: str,
        expected_effect: str,
        null_hypothesis: str,
        variables: List[str],
        dataset: str,
        features: List[str],
        model: str,
        time_period: str = "2021-2026",
        auto_approve: bool = True,
    ) -> Dict[str, Any]:
        """Runs complete end-to-end research intelligence workflow from Hypothesis to Report."""
        # 1. Hypothesis Registration & Pre-registration
        prereg = PreRegistrationSpec(
            objective=description,
            dataset=dataset,
            features=features,
            model=model,
            evaluation_metrics=["sharpe", "cagr", "directional_accuracy"],
            period=time_period,
            expected_relationship=expected_effect,
        )
        hypo = self.hypothesis_registry.register(
            title=title,
            description=description,
            research_question=research_question,
            expected_effect=expected_effect,
            null_hypothesis=null_hypothesis,
            variables=variables,
            dataset=dataset,
            time_period=time_period,
            preregistration=prereg,
        )

        # 2. Base Experiment Config Creation
        config = ExperimentConfig(
            name=f"Exp_{title.replace(' ', '_')}",
            hypothesis_id=hypo.hypothesis_id,
            dataset=dataset,
            features=features,
            model=model,
        )

        # 3. Create & Approve Experiment
        exp_record = self.experiment_manager.create_experiment(
            config, priority=ExperimentPriority.HIGH, auto_approve=auto_approve
        )
        self.hypothesis_registry.attach_experiment(hypo.hypothesis_id, exp_record.experiment_id)

        # 4. Run Base Experiment
        base_results = self.experiment_runner.run_experiment(exp_record.experiment_id)

        # 5. Diagnostic Error Analysis
        diagnostics = self.error_analyzer.analyze_experiment_errors(
            exp_record.experiment_id, features
        )

        # 6. Ablation Study
        ablation_summary = self.ablation_engine.run_ablation_study(
            config, hypo.hypothesis_id, auto_approve=auto_approve
        )

        # 7. Robustness Test
        robustness_summary = self.robustness_engine.run_robustness_suite(
            config, hypo.hypothesis_id, auto_approve=auto_approve
        )

        # 8. Store Research Findings in Memory
        sharpe = base_results.get("trading_metrics", {}).get("sharpe", 0.0)
        finding_stmt = f"Observed Sharpe ratio of {sharpe:.2f} for model {model} on dataset {dataset}."
        finding = self.research_memory.store_finding(
            experiment_id=exp_record.experiment_id,
            statement=finding_stmt,
            evidence=f"Backtest Sharpe {sharpe:.2f}, Accuracy {base_results.get('prediction_metrics', {}).get('directional_accuracy', 0.5):.2%}.",
            metrics=base_results,
            period=time_period,
            confidence=0.85,
            limitations="Simulated paper-trading environment only; subject to market regime shifts.",
        )

        # Update hypothesis state
        self.hypothesis_registry.update_status(hypo.hypothesis_id, HypothesisState.SUPPORTED)

        # 9. Generate Recommendations
        recommendations = self.recommendation_engine.generate_recommendations(
            exp_record, ablation_summary, robustness_summary
        )

        # 10. Generate Markdown Reports
        report_path = self.report_generator.generate_experiment_report(exp_record)

        summary_data = {
            "hypotheses_count": len(self.hypothesis_registry.list_hypotheses()),
            "experiments_count": len(self.experiment_manager.list_all()),
            "findings_count": len(self.research_memory._findings),
            "failures_count": len(self.research_memory._failures),
            "findings_text": f"- [{finding.finding_id}] {finding.statement}",
        }
        self.report_generator.generate_research_summary(summary_data)

        return {
            "hypothesis": hypo.to_dict(),
            "experiment": exp_record.to_dict(),
            "base_results": base_results,
            "diagnostics": diagnostics,
            "ablation": ablation_summary,
            "robustness": robustness_summary,
            "finding": finding.to_dict(),
            "recommendations": recommendations,
            "report_path": report_path,
        }
