"""
Risk & Stress Testing Report Generator for Advanced Risk Engine OS.
"""

from typing import Dict, Any


class RiskReportGenerator:
    """Generates markdown reports summarizing market risk, tail risk, stress testing, and Monte Carlo."""

    @staticmethod
    def generate_report_md(risk_result: Dict[str, Any]) -> str:
        risk_id = risk_result.get("risk_id", "N/A")
        port_id = risk_result.get("portfolio_id", "N/A")
        mkt = risk_result.get("market_risk", {})
        tail = risk_result.get("tail_risk", {})
        dd = risk_result.get("drawdown_analysis", {})
        mc = risk_result.get("monte_carlo_results", {})
        limits = risk_result.get("risk_limits_status", {})
        stress = risk_result.get("stress_results", {}).get("stress_results", {})

        md_lines = [
            f"# Advanced Quantitative Risk & Stress Testing Report",
            f"**Risk Analysis ID**: `{risk_id}` | **Portfolio ID**: `{port_id}`",
            f"**Timestamp**: `{risk_result.get('timestamp', 'N/A')}`",
            "",
            "## 1. Market & Tail Risk Overview",
            f"- **Historical Volatility (Annual)**: {mkt.get('historical_volatility', 0.0)*100.0:.2f}%",
            f"- **EWMA Volatility**: {mkt.get('ewma_volatility', 0.0)*100.0:.2f}%",
            f"- **Portfolio Beta**: {mkt.get('beta', 1.0):.2f}",
            f"- **Value at Risk (VaR 95% 1D)**: {tail.get('var_95_historical', 0.0)*100.0:.2f}%",
            f"- **Conditional VaR (CVaR 95% 1D)**: {tail.get('cvar_95', 0.0)*100.0:.2f}%",
            f"- **Maximum Drawdown**: {dd.get('max_drawdown', 0.0)*100.0:.2f}%",
            f"- **Max Drawdown Duration**: {dd.get('max_duration_days', 0)} days",
            "",
            "## 2. Monte Carlo Simulation (10,000 Paths)",
            f"- **Monte Carlo VaR 95%**: ${mc.get('mc_var_95', 0.0):,.2f}",
            f"- **Monte Carlo CVaR 95%**: ${mc.get('mc_cvar_95', 0.0):,.2f}",
            f"- **Expected Mean P&L**: ${mc.get('mean_pnl', 0.0):,.2f}",
            f"- **5th Percentile P&L**: ${mc.get('quantile_5pct', 0.0):,.2f}",
            "",
            "## 3. Stress Testing Scenario Matrix",
            "| Scenario ID | Stressed Value | Absolute Loss | Loss (%) |",
            "| :--- | :---: | :---: | :---: |",
        ]

        for s_id, s_res in stress.items():
            val = s_res.get("stressed_value", 0.0)
            loss = s_res.get("absolute_loss", 0.0)
            loss_pct = s_res.get("percentage_loss", 0.0) * 100.0
            md_lines.append(f"| `{s_id}` | ${val:,.2f} | ${loss:,.2f} | {loss_pct:.2f}% |")

        md_lines.extend([
            "",
            "## 4. Risk Limit Compliance",
            f"- **Status**: `{limits.get('status', 'NORMAL')}`",
        ])

        breaches = limits.get("breaches", [])
        if breaches:
            md_lines.append("### Active Limit Breaches:")
            for b in breaches:
                md_lines.append(f"- ⚠️ `{b}`")
        else:
            md_lines.append("- ✅ All volatility, VaR, CVaR, drawdown, and leverage limits satisfied.")

        return "\n".join(md_lines)
