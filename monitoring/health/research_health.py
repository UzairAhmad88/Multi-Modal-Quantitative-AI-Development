"""
Composite Research Health Index Engine.
"""

from typing import Dict, Any, List, Optional
from ..core.monitor_result import ResearchHealthScore, DriftMetricResult, ConceptDriftResult, AlphaDecayResult, RegimeShiftResult


def calculate_research_health_score(
    data_quality: Dict[str, Any],
    drift_results: List[DriftMetricResult],
    concept_results: List[ConceptDriftResult],
    alpha_decay: Optional[AlphaDecayResult] = None,
    regime_shift: Optional[RegimeShiftResult] = None,
    component_weights: Optional[Dict[str, float]] = None,
) -> ResearchHealthScore:
    """Computes composite Research Health Score (0-100)."""
    weights = component_weights or {
        "data_quality": 0.20,
        "feature_stability": 0.20,
        "concept_stability": 0.20,
        "alpha_retention": 0.20,
        "risk_compliance": 0.20,
    }

    # 1. Data Quality Score
    dq_score = float(data_quality.get("data_quality_score", 100.0))

    # 2. Feature Stability Score
    if drift_results:
        drifted_count = sum(1 for d in drift_results if d.is_drifted)
        feat_score = max(0.0, 100.0 * (1.0 - (drifted_count / len(drift_results))))
    else:
        feat_score = 100.0

    # 3. Concept Stability Score
    if concept_results:
        concept_drift_count = sum(1 for c in concept_results if c.drift_detected)
        concept_score = max(0.0, 100.0 * (1.0 - (concept_drift_count / len(concept_results))))
    else:
        concept_score = 100.0

    # 4. Alpha Retention Score
    if alpha_decay:
        alpha_score = max(0.0, 100.0 * (1.0 - max(0.0, alpha_decay.ic_decay_pct)))
    else:
        alpha_score = 100.0

    # 5. Risk Compliance Score
    if regime_shift and regime_shift.is_regime_shift_detected:
        risk_score = 70.0
    else:
        risk_score = 100.0

    overall_score = (
        weights["data_quality"] * dq_score
        + weights["feature_stability"] * feat_score
        + weights["concept_stability"] * concept_score
        + weights["alpha_retention"] * alpha_score
        + weights["risk_compliance"] * risk_score
    )

    if overall_score >= 80.0:
        status = "HEALTHY"
        summary = f"Research system is HEALTHY with composite score {overall_score:.1f}/100."
    elif overall_score >= 60.0:
        status = "WARNING"
        summary = f"Research system shows MODERATE DRIFT/DECAY with composite score {overall_score:.1f}/100."
    else:
        status = "CRITICAL"
        summary = f"Research system has CRITICAL DRIFT/DECAY with composite score {overall_score:.1f}/100."

    return ResearchHealthScore(
        overall_health_score=round(overall_score, 2),
        data_quality_score=round(dq_score, 2),
        feature_stability_score=round(feat_score, 2),
        concept_stability_score=round(concept_score, 2),
        alpha_retention_score=round(alpha_score, 2),
        risk_compliance_score=round(risk_score, 2),
        status=status,
        summary=summary,
    )
