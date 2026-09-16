"""
Master Research Intelligence Engine for Multi-Modal Quant AI.
Orchestrates pattern discovery, hypothesis generation, experiment creation, research graph building, evidence classification, and reporting.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from research_intelligence.discovery.pattern_discovery import PatternDiscoveryEngine
from research_intelligence.patterns.event_study import EventStudyEngine
from research_intelligence.patterns.regime_discovery import RegimeDiscoveryEngine
from research_intelligence.hypotheses.hypothesis_engine import HypothesisEngine, ResearchHypothesis
from research_intelligence.experiment_generation.generator import ExperimentGenerator
from research_intelligence.evidence.evidence_engine import EvidenceEngine
from research_intelligence.evidence.research_memory import ResearchMemory
from research_intelligence.attribution.error_analyzer import ModelErrorAnalyzer
from research_intelligence.similarity.similarity import ResearchSimilarityEngine
from research_intelligence.research_graph.graph import ResearchGraph, NodeType, EdgeType
from research_intelligence.ranking.research_priority import ResearchPriorityOrganizer
from research_intelligence.reports.report_generator import ResearchIntelligenceReportGenerator
from research_intelligence.prompts.research_prompts import PromptGenerator
from research_intelligence.utils.assistant import ResearchAssistant


class ResearchIntelligenceEngine:
    """Master Research Intelligence Engine coordinating automated research discovery and analysis."""

    def __init__(self):
        self.pattern_discovery = PatternDiscoveryEngine()
        self.event_study = EventStudyEngine()
        self.regime_discovery = RegimeDiscoveryEngine()
        self.hypothesis_engine = HypothesisEngine()
        self.experiment_generator = ExperimentGenerator()
        self.evidence_engine = EvidenceEngine()
        self.memory = ResearchMemory()
        self.error_analyzer = ModelErrorAnalyzer()
        self.similarity_engine = ResearchSimilarityEngine()
        self.graph = ResearchGraph()
        self.priority_organizer = ResearchPriorityOrganizer()
        self.report_generator = ResearchIntelligenceReportGenerator()
        self.prompt_generator = PromptGenerator()
        self.assistant = ResearchAssistant()

    def discover_and_hypothesize(self, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Runs pattern discovery and auto-generates testable hypotheses."""
        patterns_res = self.pattern_discovery.discover_patterns(combined_df=df)
        hypotheses = self.hypothesis_engine.generate_hypotheses_from_patterns(patterns_res)

        # Record in Research Graph and Memory
        for hyp in hypotheses:
            self.memory.record_hypothesis(hyp.to_dict())
            self.graph.add_node(hyp.hypothesis_id, NodeType.HYPOTHESIS, hyp.statement, hyp.to_dict())

        return {
            "patterns": patterns_res.get("patterns", []),
            "anomalies": patterns_res.get("anomalies", []),
            "generated_hypotheses": [h.to_dict() for h in hypotheses],
            "total_hypotheses": len(hypotheses)
        }

    def generate_experiment_for_hypothesis(
        self,
        hypothesis_id: str,
        symbols: Optional[list] = None,
        model_type: str = "multimodal"
    ) -> Dict[str, Any]:
        """Converts hypothesis into executable experiment config and registers graph relationships."""
        hyp = self.hypothesis_engine.get_hypothesis(hypothesis_id)
        if not hyp:
            raise ValueError(f"Hypothesis '{hypothesis_id}' not found.")

        config = self.experiment_generator.generate_experiment_config(hyp, symbols=symbols, model_type=model_type)
        yaml_path = self.experiment_generator.save_experiment_yaml(hyp, config)

        exp_node_id = f"EXP-{hyp.hypothesis_id}"
        self.graph.add_node(exp_node_id, NodeType.EXPERIMENT, config["experiment"]["name"], config)
        self.graph.add_edge(hyp.hypothesis_id, exp_node_id, EdgeType.TESTED_BY)

        # Duplicate check
        similar = self.similarity_engine.find_similar_experiments(config)

        return {
            "hypothesis_id": hypothesis_id,
            "experiment_id": exp_node_id,
            "config_yaml_path": yaml_path,
            "config": config,
            "similar_experiments": similar
        }

    def evaluate_and_record_finding(
        self,
        hypothesis_id: str,
        experiment_id: str,
        metrics: Dict[str, Any],
        observation: str = "Automated experiment execution completed."
    ) -> Dict[str, Any]:
        """Evaluates metrics, classifies evidence, updates research graph, memory, and compiles report."""
        evidence = self.evidence_engine.classify_evidence(metrics)
        finding_id = f"FND-{experiment_id}"

        hyp = self.hypothesis_engine.get_hypothesis(hypothesis_id)
        hyp_dict = hyp.to_dict() if hyp else {"hypothesis_id": hypothesis_id, "statement": "N/A"}

        self.memory.record_finding(
            finding_id=finding_id,
            hypothesis_id=hypothesis_id,
            experiment_id=experiment_id,
            observation=observation,
            evidence_status=evidence["status"],
            metrics=metrics,
            limitations=evidence.get("limitations", [])
        )

        self.graph.add_node(finding_id, NodeType.FINDING, observation, evidence)
        self.graph.add_edge(experiment_id, finding_id, EdgeType.SUPPORTS)

        questions = self.prompt_generator.generate_follow_up_questions(
            hyp_dict.get("statement", ""),
            evidence["status"],
            metrics
        )

        report_path = self.report_generator.generate_report(
            experiment_id=experiment_id,
            hypothesis=hyp_dict,
            patterns=[],
            evidence=evidence,
            questions=questions
        )

        return {
            "finding_id": finding_id,
            "evidence_status": evidence["status"],
            "evidence": evidence,
            "report_path": report_path,
            "follow_up_questions": questions
        }
