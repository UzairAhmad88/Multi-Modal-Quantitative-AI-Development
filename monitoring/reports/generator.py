"""
Markdown Monitoring & Drift Report Generator.
"""

from typing import Optional
from ..core.monitor_result import MonitoringResult


class MonitoringReportGenerator:
    """Generates structured Markdown reports for model monitoring and drift audits."""

    def generate_markdown_report(self, result: MonitoringResult) -> str:
        lines = [
            f"# Model Monitoring & Research Health Audit Report: {result.monitoring_id}",
            "",
            f"- **Experiment ID**: `{result.experiment_id}`",
            f"- **Timestamp**: `{result.timestamp}`",
            f"- **Research Health Score**: **{result.health_score.overall_health_score:.1f} / 100** (`{result.health_score.status}`)",
            f"- **Summary**: {result.health_score.summary}",
            "",
            "---",
            "",
            "## 1. Research Health Breakdown",
            "",
            "| Component | Score (0 - 100) | Status |",
            "| :--- | :---: | :---: |",
            f"| Data Quality | `{result.health_score.data_quality_score:.1f}` | {'PASS' if result.health_score.data_quality_score >= 80 else 'WARN'} |",
            f"| Feature Stability | `{result.health_score.feature_stability_score:.1f}` | {'PASS' if result.health_score.feature_stability_score >= 80 else 'WARN'} |",
            f"| Concept Stability | `{result.health_score.concept_stability_score:.1f}` | {'PASS' if result.health_score.concept_stability_score >= 80 else 'WARN'} |",
            f"| Alpha Retention | `{result.health_score.alpha_retention_score:.1f}` | {'PASS' if result.health_score.alpha_retention_score >= 80 else 'WARN'} |",
            f"| Risk Compliance | `{result.health_score.risk_compliance_score:.1f}` | {'PASS' if result.health_score.risk_compliance_score >= 80 else 'WARN'} |",
            "",
            "---",
            "",
            "## 2. Data Drift Audit Results",
            "",
            "| Feature Name | PSI Score | KS Statistic | KS p-value | Wasserstein Dist | Severity | Status |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]

        for d in result.data_drift_results:
            status_str = "DRIFTED" if d.is_drifted else "STABLE"
            lines.append(
                f"| `{d.feature_name}` | `{d.psi_score:.4f}` | `{d.ks_statistic:.4f}` | `{d.ks_pvalue:.4e}` | `{d.wasserstein_distance:.4f}` | `{d.severity}` | **{status_str}** |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 3. Active Monitoring Alerts",
            "",
        ])

        if result.alerts:
            for alert in result.alerts:
                lines.append(f"- `[{alert.severity}]` **{alert.component}**: {alert.message}")
        else:
            lines.append("No active alerts triggered.")

        lines.extend([
            "",
            "---",
            "",
            "> [!NOTE]",
            "> All drift metrics and health scores are for quantitative research, model health diagnostics, and adaptive strategy monitoring. Real-money live trading remains STRICTLY DISABLED.",
        ])

        return "\n".join(lines)
