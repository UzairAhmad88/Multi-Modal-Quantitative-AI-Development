"""
Portfolio Report Generator for Portfolio Construction OS.
"""

from typing import Dict, Any, List


class PortfolioReportGenerator:
    """Generates markdown reports summarizing portfolio optimization, risk attribution, and constraints."""

    @staticmethod
    def generate_report_md(opt_result: Dict[str, Any]) -> str:
        weights = opt_result.get("target_weights", {})
        risk = opt_result.get("risk_attribution", {})
        cost = opt_result.get("transaction_costs", {})
        conc = risk.get("concentration_metrics", {})
        constraints = opt_result.get("constraint_status", {})

        md_lines = [
            f"# Portfolio Construction & Optimization Report",
            f"**Portfolio ID**: `{opt_result.get('portfolio_id', 'N/A')}`",
            f"**Optimization Method**: `{opt_result.get('method', 'N/A')}`",
            f"**Solver Status**: `{opt_result.get('solver_status', 'N/A')}`",
            f"**Timestamp**: `{opt_result.get('timestamp', 'N/A')}`",
            "",
            "## 1. Target Portfolio Allocations",
            "| Asset | Target Weight | PCR (Risk %) |",
            "| :--- | :---: | :---: |",
        ]

        pcr = risk.get("asset_risk_contributions", {})
        for asset, w in weights.items():
            risk_pct = pcr.get(asset, 0.0) * 100.0
            md_lines.append(f"| `{asset}` | {w*100.0:.2f}% | {risk_pct:.2f}% |")

        md_lines.extend([
            "",
            "## 2. Risk & Concentration Summary",
            f"- **Portfolio Volatility**: {risk.get('portfolio_volatility', 0.0)*100.0:.2f}%",
            f"- **Diversification Ratio**: {risk.get('diversification_ratio', 1.0):.4f}",
            f"- **Herfindahl Index (HHI)**: {conc.get('hhi', 0.0):.4f}",
            f"- **Effective Assets (N_eff)**: {conc.get('effective_n', 0.0):.2f}",
            f"- **Top 5 Exposure**: {conc.get('top5_exposure', 0.0)*100.0:.2f}%",
            "",
            "## 3. Transaction Costs & Turnover",
            f"- **Total Estimated Cost**: ${cost.get('total_cost', 0.0):,.2f} ({cost.get('cost_bps', 0.0):.1f} bps)",
            f"- **Total Traded Value**: ${cost.get('total_traded_value', 0.0):,.2f}",
            "",
            "## 4. Constraint Evaluation",
            f"- **Feasibility Status**: `{constraints.get('status', 'PASSED')}`",
        ])

        failed = constraints.get("failed_constraints", [])
        if failed:
            md_lines.append("### Infeasible / Warning Constraints:")
            for f_str in failed:
                md_lines.append(f"- ⚠️ {f_str}")
        else:
            md_lines.append("- ✅ All position, sector, leverage, and turnover constraints satisfied.")

        return "\n".join(md_lines)
