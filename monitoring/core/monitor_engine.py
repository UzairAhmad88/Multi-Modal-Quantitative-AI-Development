"""
Master Model Monitoring Engine Orchestrator.
"""

import datetime
import uuid
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union
from .alerts import AlertManager, AlertSeverity
from .monitor_result import (
    MonitoringResult,
    DriftMetricResult,
    ConceptDriftResult,
    AlphaDecayResult,
    RegimeShiftResult,
    ResearchHealthScore,
)
class ModelMonitorEngine:
    """Master Model Monitoring & Research Health OS Orchestrator."""

    def __init__(
        self,
        psi_warning_threshold: float = 0.10,
        psi_critical_threshold: float = 0.25,
        ks_pvalue_threshold: float = 0.05,
        alpha_decay_threshold: float = 0.30,
    ):
        from ..data_drift.detector import DataDriftDetector
        from ..feature_drift.feature_monitor import FeatureDriftMonitor
        from ..prediction_drift.output_monitor import OutputPredictionMonitor
        from ..performance.alpha_decay import AlphaDecayTracker
        from ..regime.detector import RegimeChangeDetector
        from ..health.system_health import SystemHealthAuditor

        from ..concept_drift.ddm import DDM
        from ..concept_drift.eddm import EDDM
        from ..concept_drift.page_hinkley import PageHinkley
        from ..health.research_health import calculate_research_health_score

        self.data_drift_detector = DataDriftDetector(
            psi_warning_threshold=psi_warning_threshold,
            psi_critical_threshold=psi_critical_threshold,
            ks_pvalue_threshold=ks_pvalue_threshold,
        )
        self.feature_monitor = FeatureDriftMonitor()
        self.output_monitor = OutputPredictionMonitor(psi_threshold=psi_warning_threshold)
        self.alpha_tracker = AlphaDecayTracker(ic_decay_threshold_pct=alpha_decay_threshold)
        self.regime_detector = RegimeChangeDetector()
        self.system_auditor = SystemHealthAuditor()
        self._ddm_cls = DDM
        self._eddm_cls = EDDM
        self._ph_cls = PageHinkley
        self._calc_health = calculate_research_health_score



    def run_monitoring_audit(
        self,
        experiment_id: str,
        baseline_df: pd.DataFrame,
        target_df: pd.DataFrame,
        baseline_predictions: Optional[np.ndarray] = None,
        target_predictions: Optional[np.ndarray] = None,
        baseline_signals: Optional[np.ndarray] = None,
        target_signals: Optional[np.ndarray] = None,
        baseline_returns: Optional[np.ndarray] = None,
        target_returns: Optional[np.ndarray] = None,
        baseline_importance: Optional[Dict[str, float]] = None,
        target_importance: Optional[Dict[str, float]] = None,
        feature_columns: Optional[List[str]] = None,
    ) -> MonitoringResult:
        monitoring_id = f"MON-{uuid.uuid4().hex[:8].upper()}"
        alert_mgr = AlertManager()

        # 1. Audit System Data Quality
        target_data_health = self.system_auditor.audit_data_health(target_df)
        if not target_data_health["is_data_healthy"]:
            alert_mgr.add_alert(
                alert_id=f"ALT-{uuid.uuid4().hex[:6]}",
                component="SYSTEM_HEALTH",
                severity=AlertSeverity.WARNING,
                message=f"Target dataset has high missing ratio: {target_data_health['missing_ratio']:.2%}",
                metric_name="missing_ratio",
                observed_value=target_data_health["missing_ratio"],
                threshold=0.10,
            )

        # 2. Audit Multi-Feature Data Drift
        drift_results = self.data_drift_detector.evaluate_feature_drift(
            baseline_df=baseline_df,
            target_df=target_df,
            feature_columns=feature_columns,
        )

        for d in drift_results:
            if d.severity == "SIGNIFICANT":
                alert_mgr.add_alert(
                    alert_id=f"ALT-{uuid.uuid4().hex[:6]}",
                    component="DATA_DRIFT",
                    severity=AlertSeverity.CRITICAL,
                    message=f"Significant data drift detected in feature '{d.feature_name}' (PSI={d.psi_score:.4f}, KS p={d.ks_pvalue:.4e})",
                    metric_name=f"psi_{d.feature_name}",
                    observed_value=d.psi_score,
                    threshold=0.25,
                    evidence=d.evidence,
                )
            elif d.severity == "MODERATE":
                alert_mgr.add_alert(
                    alert_id=f"ALT-{uuid.uuid4().hex[:6]}",
                    component="DATA_DRIFT",
                    severity=AlertSeverity.WARNING,
                    message=f"Moderate data drift detected in feature '{d.feature_name}' (PSI={d.psi_score:.4f})",
                    metric_name=f"psi_{d.feature_name}",
                    observed_value=d.psi_score,
                    threshold=0.10,
                    evidence=d.evidence,
                )

        # 3. Audit Concept Drift (if predictions and returns are available)
        concept_results = []
        if target_predictions is not None and target_returns is not None:
            # Binary directional prediction errors
            actual_dir = np.sign(target_returns)
            pred_dir = np.sign(target_predictions)
            errors = (actual_dir != pred_dir).astype(int)

            ddm = self._ddm_cls()
            ddm_warning, ddm_drift, ddm_idx = ddm.run_batch(errors)

            concept_results.append(
                ConceptDriftResult(
                    method="DDM",
                    drift_detected=ddm_drift,
                    warning_detected=ddm_warning,
                    change_point_index=ddm_idx if ddm_drift else None,
                    metric_name="prediction_error_rate",
                    current_value=float(np.mean(errors)) if len(errors) > 0 else 0.0,
                    threshold=0.50,
                    evidence={"drift_index": ddm_idx},
                )
            )

            if ddm_drift:
                alert_mgr.add_alert(
                    alert_id=f"ALT-{uuid.uuid4().hex[:6]}",
                    component="CONCEPT_DRIFT",
                    severity=AlertSeverity.CRITICAL,
                    message=f"DDM Concept Drift detected in prediction error stream at index {ddm_idx}",
                    metric_name="ddm_concept_drift",
                )

            ph = self._ph_cls()
            ph_drift, ph_idx = ph.run_batch(target_returns)
            concept_results.append(
                ConceptDriftResult(
                    method="PAGE_HINKLEY",
                    drift_detected=ph_drift,
                    warning_detected=False,
                    change_point_index=ph_idx if ph_drift else None,
                    metric_name="cumulative_return_shift",
                    current_value=float(np.mean(target_returns)) if len(target_returns) > 0 else 0.0,
                    threshold=50.0,
                    evidence={"change_point_index": ph_idx},
                )
            )

        # 4. Audit Alpha Decay (if signals & returns provided)
        alpha_decay_res = None
        if (
            baseline_signals is not None
            and baseline_returns is not None
            and target_signals is not None
            and target_returns is not None
        ):
            alpha_decay_res = self.alpha_tracker.evaluate_alpha_decay(
                baseline_signals=baseline_signals,
                baseline_returns=baseline_returns,
                target_signals=target_signals,
                target_returns=target_returns,
            )

            if alpha_decay_res.is_decay_flagged:
                alert_mgr.add_alert(
                    alert_id=f"ALT-{uuid.uuid4().hex[:6]}",
                    component="ALPHA_DECAY",
                    severity=AlertSeverity.CRITICAL,
                    message=f"Alpha decay detected: IC dropped {alpha_decay_res.ic_decay_pct:.2%}, Sharpe dropped {alpha_decay_res.sharpe_decay_pct:.2%}",
                    metric_name="ic_decay_pct",
                    observed_value=alpha_decay_res.ic_decay_pct,
                    threshold=0.30,
                )

        # 5. Audit Macro Regime Shift
        regime_shift_res = None
        if baseline_returns is not None and target_returns is not None:
            regime_shift_res = self.regime_detector.detect_regime_shift(
                baseline_returns=baseline_returns,
                target_returns=target_returns,
            )
            if regime_shift_res.is_regime_shift_detected:
                alert_mgr.add_alert(
                    alert_id=f"ALT-{uuid.uuid4().hex[:6]}",
                    component="REGIME_SHIFT",
                    severity=AlertSeverity.WARNING,
                    message=f"Macro regime shift detected: {regime_shift_res.current_regime} (Vol Ratio={regime_shift_res.volatility_jump_ratio:.2f})",
                    metric_name="volatility_jump_ratio",
                    observed_value=regime_shift_res.volatility_jump_ratio,
                    threshold=2.0,
                )

        # 6. Calculate Composite Research Health Score
        health_score = self._calc_health(
            data_quality=target_data_health,
            drift_results=drift_results,
            concept_results=concept_results,
            alpha_decay=alpha_decay_res,
            regime_shift=regime_shift_res,
        )

        if health_score.status == "CRITICAL":
            alert_mgr.add_alert(
                alert_id=f"ALT-{uuid.uuid4().hex[:6]}",
                component="RESEARCH_HEALTH",
                severity=AlertSeverity.CRITICAL,
                message=health_score.summary,
                metric_name="overall_health_score",
                observed_value=health_score.overall_health_score,
                threshold=60.0,
            )

        return MonitoringResult(
            monitoring_id=monitoring_id,
            experiment_id=experiment_id,
            baseline_dataset_id="BASELINE-001",
            target_dataset_id="TARGET-001",
            data_drift_results=drift_results,
            concept_drift_results=concept_results,
            alpha_decay=alpha_decay_res,
            regime_shift=regime_shift_res,
            health_score=health_score,
            alerts=alert_mgr.get_alerts(),
        )
