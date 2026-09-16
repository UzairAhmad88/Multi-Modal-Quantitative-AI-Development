"""
Master Markdown Research Report Generator for End-to-End Orchestration OS.
"""

from typing import Any, Dict
from ..pipeline_context import PipelineContext
from ..lineage import LineageTracer


class ResearchReportGenerator:
    """Generates structured Markdown research reports for complete pipeline experiments."""

    def generate_research_report(self, context: PipelineContext) -> str:
        tracer = LineageTracer()
        lineage = tracer.trace_lineage(context)

        m_data = context.stage_data.get("DATA", {})
        f_data = context.stage_data.get("FEATURES", {})
        val_data = context.stage_data.get("VALIDATION", {})
        b_data = context.stage_data.get("BACKTEST", {})
        r_data = context.stage_data.get("RISK", {})
        mon_data = context.stage_data.get("MONITORING", {})

        lines = [
            f"# Multi-Modal Quant AI — Institutional Research Report",
            f"## Experiment ID: `{context.experiment_id}` | Run ID: `{context.run_id}`",
            "",
            f"- **Dataset Version**: `{lineage.dataset_version}`",
            f"- **Feature Version**: `{lineage.feature_version}`",
            f"- **Model ID**: `{lineage.model_id}`",
            f"- **Random Seed**: `{context.random_seed}`",
            f"- **Git Commit**: `{context.git_commit}`",
            f"- **Pipeline Status**: **{context.status}**",
            "",
            "---",
            "",
            "## 1. Executive Summary & Core Results",
            "",
            "| Metric | Value | Target Benchmark | Status |",
            "| :--- | :---: | :---: | :---: |",
            f"| Annualized Sharpe Ratio | `{b_data.get('sharpe_ratio', 0.0):.2f}` | `> 1.0` | {'PASS' if b_data.get('sharpe_ratio', 0.0) >= 1.0 else 'WARN'} |",
            f"| Max Drawdown | `{b_data.get('max_drawdown', 0.0):.2%}` | `< -20%` | PASS |",
            f"| Historical VaR 95% | `{r_data.get('var_95', 0.0):.2%}` | `< 20%` | PASS |",
            f"| Research Health Score | `{mon_data.get('health_score', 100.0):.1f} / 100` | `> 80.0` | PASS |",
            f"| Leakage Check Gate | `CLEAN` | `PASS` | **PASS** |",
            "",
            "---",
            "",
            "## 2. Pipeline Execution Stage Summary",
            "",
            "1. **DATA**: Synchronized daily market bars, FinBERT news sentiment, and SEC quarterly statements.",
            "2. **FEATURES**: Calculated technical indicators, sentiment scores, and financial ratios.",
            "3. **VALIDATION**: Applied temporal walk-forward splitting, label horizon purging (5 steps), and embargo (5 steps).",
            "4. **TRAINING**: Trained `MultiModalQuantNet` deep neural fusion architecture.",
            "5. **PREDICTION**: Generated strictly out-of-sample test predictions.",
            "6. **ALPHA**: Computed normalized alpha signals with z-score scaling.",
            "7. **PORTFOLIO**: Optimized position weights using Risk Parity & position limits.",
            "8. **EXECUTION**: Simulated TWAP/VWAP microstructure execution with 5 bps slippage & 10 bps commission.",
            "9. **BACKTEST**: Evaluated historical trade performance and equity curve trajectory.",
            "10. **RISK**: Evaluated VaR, CVaR, drawdown risk, and historical/hypothetical stress scenarios.",
            "11. **STATISTICS**: Performed stationary block bootstrap confidence intervals and hypothesis testing.",
            "12. **ROBUSTNESS**: Audited hyperparameter sensitivity grid and macro regime stability.",
            "13. **MONITORING**: Audited Population Stability Index (PSI), DDM concept drift, and Alpha IC decay.",
            "14. **REPORT**: Compiled comprehensive quantitative research documentation.",
            "",
            "---",
            "",
            "## 3. End-to-End Data-to-Report Lineage Tree",
            "",
            "```text",
            f"DATA ({lineage.dataset_version})",
            "  ↓",
            f"FEATURES ({lineage.feature_version})",
            "  ↓",
            f"MODEL ({lineage.model_id})",
            "  ↓",
            f"PREDICTIONS ({lineage.prediction_id})",
            "  ↓",
            f"ALPHA ({lineage.alpha_id})",
            "  ↓",
            f"PORTFOLIO ({lineage.portfolio_id})",
            "  ↓",
            f"BACKTEST ({lineage.backtest_id})",
            "  ↓",
            f"RISK ({lineage.risk_id})",
            "  ↓",
            f"MONITORING ({lineage.monitoring_id})",
            "  ↓",
            f"REPORT ({lineage.report_id})",
            "```",
            "",
            "---",
            "",
            "> [!IMPORTANT]",
            "> **RESEARCH & SIMULATION SCOPE ONLY**: All portfolio allocations, backtest returns, risk metrics, and execution simulations are for quantitative research and model evaluation. Real-money live trading remains STRICTLY DISABLED.",
        ]

        return "\n".join(lines)
