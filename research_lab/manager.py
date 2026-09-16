"""
Experiment Manager: Central Facade for Research Laboratory Experiment Tracking, Intelligence, and Lineage.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import numpy as np

from research_lab.experiments.states import ExperimentStatus, RunStatus
from research_lab.schemas.experiment_schema import Experiment
from research_lab.hypotheses.hypothesis_manager import HypothesisManager, Hypothesis
from research_lab.runs.experiment_run import ExperimentRun
from research_lab.tracking.metric_store import MetricStore
from research_lab.artifacts.artifact_store import ArtifactStore
from research_lab.lineage.lineage_graph import LineageGraph
from research_lab.comparison.comparison_engine import ExperimentComparisonEngine
from research_lab.comparison.experiment_diff import ExperimentDiff
from research_lab.knowledge_base.knowledge_base import ResearchKnowledgeBase
from research_lab.knowledge_base.findings import Finding
from research_lab.intelligence.research_intelligence_engine import ResearchIntelligenceEngine
from research_lab.reproducibility.reproducibility_checker import ReproducibilityChecker
from research_lab.reproducibility.replication import ReplicationExperiment
from research_lab.experiments.templates import get_template
from research_lab.reports.experiment_report import ExperimentReportBuilder

# Integration with Phase 20 research evaluation manager
from research_evaluation.manager import ResearchEvaluationManager


class ExperimentManager:
    """Master Orchestrator for Phase 21 Systematic Research Laboratory OS."""

    def __init__(self):
        self.hypothesis_mgr = HypothesisManager()
        self.metric_store = MetricStore()
        self.artifact_store = ArtifactStore()
        self.lineage_graph = LineageGraph()
        self.comparison_engine = ExperimentComparisonEngine()
        self.diff_engine = ExperimentDiff()
        self.knowledge_base = ResearchKnowledgeBase()
        self.intelligence_engine = ResearchIntelligenceEngine()
        self.repro_checker = ReproducibilityChecker()
        self.replication_engine = ReplicationExperiment()
        self.report_builder = ExperimentReportBuilder()
        self.eval_manager = ResearchEvaluationManager()

        self.experiments: Dict[str, Experiment] = {}
        self.runs: Dict[str, List[ExperimentRun]] = {}
        self.experiment_results: Dict[str, Dict[str, Any]] = {}

    def create_experiment(
        self,
        name: str = "Multimodal Alpha Experiment",
        template_name: str = "multimodal",
        hypothesis: Optional[Dict[str, str]] = None,
        custom_config: Optional[Dict[str, Any]] = None,
        random_seed: int = 42
    ) -> Experiment:
        """Creates a new experiment from template and registers configuration hash."""
        exp_id = f"EXP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        base_config = get_template(template_name)
        if custom_config:
            base_config.update(custom_config)

        default_hyp = {
            "research_question": "Does multimodal data integration improve out-of-sample Sharpe ratio?",
            "hypothesis": "Fusing news NLP and fundamentals with technicals increases risk-adjusted return.",
            "null_hypothesis": "Multimodal fusion provides no statistically significant alpha improvement.",
            "success_criteria": "Out-of-sample Sharpe Ratio >= 1.25 with p-value < 0.05"
        }

        exp = Experiment(
            experiment_id=exp_id,
            name=name,
            description=f"Experiment based on template '{template_name}'",
            hypothesis=hypothesis or default_hyp,
            dataset_id=base_config.get("dataset_id", "DS-SP500_MULTIMODAL"),
            feature_version=base_config.get("feature_version", "v2.5.0"),
            model_version=base_config.get("model_version", "MultiModalQuantNet"),
            strategy_id=base_config.get("strategy_id", "MULTIMODAL_FUSION_ALPHA"),
            portfolio_config=base_config.get("portfolio_config", {"method": "target_volatility"}),
            execution_config=base_config.get("execution_config", {"algorithm": "VWAP"}),
            evaluation_config=base_config.get("evaluation_config", {"walk_forward": True}),
            random_seed=random_seed,
            status=ExperimentStatus.READY,
            tags=[template_name, "multimodal", base_config.get("model_version", "model")]
        )
        exp.compute_config_hash()

        self.experiments[exp_id] = exp
        self.runs[exp_id] = []
        return exp

    def run_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Executes an experiment run across backtest, portfolio, execution, and research evaluation."""
        if experiment_id not in self.experiments:
            exp = self.create_experiment(name=f"Auto Experiment {experiment_id}")
            experiment_id = exp.experiment_id
        else:
            exp = self.experiments[experiment_id]

        exp.status = ExperimentStatus.RUNNING
        run = ExperimentRun(experiment_id=experiment_id, random_seed=exp.random_seed, status=RunStatus.RUNNING)

        try:
            # Execute Phase 20 research evaluation as pipeline backbone
            eval_res = self.eval_manager.evaluate_strategy(strategy_id=exp.strategy_id)

            perf = eval_res["performance"]
            metrics = {
                "cagr": perf["cagr"],
                "sharpe_ratio": perf["sharpe_ratio"],
                "sortino_ratio": perf["sortino_ratio"],
                "max_drawdown": perf["max_drawdown"],
                "win_rate": perf["win_rate"],
                "profit_factor": perf["profit_factor"],
                "robustness_score": eval_res["robustness"]["robustness_score"]
            }

            # Register metrics into metric store
            for k, v in metrics.items():
                self.metric_store.log_metric(experiment_id, run.run_id, k, v)

            # Register artifacts
            art_report = self.artifact_store.register_artifact(
                experiment_id, "REPORT", f"reports/research/{experiment_id}_report.md", "Evaluation Report"
            )

            run.complete_run(metrics=metrics, artifacts={"report": art_report["file_path"]})
            exp.status = ExperimentStatus.COMPLETED

            # Lineage DAG
            lineage = self.lineage_graph.build_lineage(
                experiment_id=exp.experiment_id,
                dataset_id=exp.dataset_id,
                feature_version=exp.feature_version,
                model_version=exp.model_version,
                strategy_id=exp.strategy_id,
                portfolio_id="PORTFOLIO-001",
                execution_id="EXEC-001",
                backtest_id="BT-001",
                evaluation_id=eval_res["evaluation_id"],
                report_id=f"REP-{exp.experiment_id}"
            )

            result = {
                "experiment_id": exp.experiment_id,
                "name": exp.name,
                "status": exp.status.value,
                "configuration_hash": exp.configuration_hash,
                "dataset_id": exp.dataset_id,
                "feature_version": exp.feature_version,
                "model_version": exp.model_version,
                "hypothesis": exp.hypothesis,
                "metrics": metrics,
                "evaluation_details": eval_res,
                "lineage": lineage,
                "run": run.to_dict()
            }

            reports = self.report_builder.build_report(result)
            result["reports"] = reports

            self.runs[experiment_id].append(run)
            self.experiment_results[experiment_id] = result

            # Register finding into Knowledge Base
            finding_stmt = f"Experiment '{exp.name}' achieved Sharpe ratio {metrics['sharpe_ratio']:.2f} with CAGR {metrics['cagr']:.2%}."
            self.knowledge_base.add_finding(Finding(experiment_id=exp.experiment_id, statement=finding_stmt, evidence=["sharpe_ratio"]))

            return result

        except Exception as e:
            run.fail_run(str(e))
            exp.status = ExperimentStatus.FAILED
            raise e

    def clone_experiment(self, experiment_id: str, new_name: Optional[str] = None) -> Experiment:
        """Clones an experiment configuration into a new immutable experiment."""
        orig = self.experiments.get(experiment_id)
        if not orig:
            orig = self.create_experiment()

        clone_name = new_name or f"Clone of {orig.name}"
        cloned = self.create_experiment(
            name=clone_name,
            hypothesis=orig.hypothesis.copy(),
            custom_config={
                "dataset_id": orig.dataset_id,
                "feature_version": orig.feature_version,
                "model_version": orig.model_version,
                "strategy_id": orig.strategy_id,
                "portfolio_config": orig.portfolio_config.copy(),
                "execution_config": orig.execution_config.copy(),
                "evaluation_config": orig.evaluation_config.copy()
            },
            random_seed=orig.random_seed
        )
        return cloned

    def replicate_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Replicates an experiment exactly to verify reproducibility."""
        orig_res = self.experiment_results.get(experiment_id)
        if not orig_res:
            orig_res = self.run_experiment(experiment_id)

        rep_runner = lambda orig: self.run_experiment(self.clone_experiment(experiment_id, new_name=f"Replication of {experiment_id}").experiment_id)
        rep_res = rep_runner(orig_res)

        status, details = self.repro_checker.verify_reproducibility(orig_res, rep_res)
        return {
            "original_experiment_id": experiment_id,
            "replication_experiment_id": rep_res["experiment_id"],
            "reproducibility_status": status,
            "details": details
        }

    def compare_experiments(self, experiment_ids: List[str]) -> Dict[str, Any]:
        """Compares multiple experiment results side-by-side."""
        exps_data = []
        for eid in experiment_ids:
            res = self.experiment_results.get(eid)
            if not res:
                res = self.run_experiment(eid)
            exps_data.append(res)

        return self.comparison_engine.compare_experiments(exps_data)
