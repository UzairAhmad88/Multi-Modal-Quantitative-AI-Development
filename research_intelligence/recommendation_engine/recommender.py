"""
Research Recommendation Engine for Research Intelligence.
Analyzes experiment history, failures, and results to suggest hypothesis refinements and research directions.
(Research directions ONLY, NEVER financial trading advice).
"""

from typing import Dict, List, Any, Optional
from research_intelligence.experiment_manager.manager import ExperimentRecord


class ResearchRecommendationEngine:
    """Generates automated quantitative research suggestions based on empirical diagnostic patterns."""

    @staticmethod
    def generate_recommendations(
        experiment: ExperimentRecord,
        ablation_summary: Optional[Dict[str, Any]] = None,
        robustness_summary: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        recommendations = []

        cfg = experiment.config
        res = experiment.results or {}
        p_metrics = res.get("prediction_metrics", {})
        t_metrics = res.get("trading_metrics", {})

        # Suggestion 1: Ablation if multi-modal features are present
        if len(cfg.features) > 2:
            recommendations.append({
                "category": "FEATURE_ABLATION",
                "recommendation": f"Run automated feature ablation study on '{cfg.name}' to quantify incremental value of news vs fundamentals.",
                "rationale": "High feature count may contain uninformative or redundant indicators.",
            })

        # Suggestion 2: Cost Sensitivity / Robustness
        turnover = t_metrics.get("turnover", 0.0)
        if turnover > 0.3:
            recommendations.append({
                "category": "ROBUSTNESS_STRESS",
                "recommendation": f"Perform transaction cost sensitivity test (1-20 bps) for '{cfg.name}'.",
                "rationale": f"Strategy turnover is elevated ({turnover:.2%}); verify edge survives slippage.",
            })

        # Suggestion 3: Model Architecture Comparison
        if cfg.model in ["LSTM", "GRU"]:
            recommendations.append({
                "category": "MODEL_COMPARISON",
                "recommendation": f"Compare '{cfg.model}' architecture against 'Transformer' or 'TabNet' on dataset '{cfg.dataset}'.",
                "rationale": "Evaluate whether attention mechanisms capture longer-term multi-modal dependencies.",
            })

        # Suggestion 4: Calibration Review
        dir_acc = p_metrics.get("directional_accuracy", 0.5)
        if dir_acc < 0.55:
            recommendations.append({
                "category": "ERROR_DIAGNOSTIC",
                "recommendation": f"Review confidence calibration and market regime breakdown for '{cfg.name}'.",
                "rationale": f"Directional accuracy ({dir_acc:.2%}) is marginal. Check performance in bear vs sideways regimes.",
            })

        if not recommendations:
            recommendations.append({
                "category": "HYPOTHESIS_EXPANSION",
                "recommendation": "Expand dataset time period and register follow-up hypothesis.",
                "rationale": "Baseline results stable.",
            })

        for rec in recommendations:
            rec["disclaimer"] = "FOR QUANTITATIVE RESEARCH PURPOSES ONLY. NOT TRADING OR INVESTMENT ADVICE."

        return recommendations
