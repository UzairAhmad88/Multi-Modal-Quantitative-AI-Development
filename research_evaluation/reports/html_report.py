"""
HTML Report Generator: Builds standalone interactive HTML research evaluation document.
"""

from typing import Dict, Any


class HTMLReportGenerator:
    """Generates standalone styled HTML report."""

    def generate_html_report(self, evaluation_result: Dict[str, Any]) -> str:
        """Builds HTML research evaluation report string."""
        eval_id = evaluation_result.get("evaluation_id", "EVAL-001")
        perf = evaluation_result.get("performance", {})
        wf = evaluation_result.get("walk_forward", {})
        boot = evaluation_result.get("bootstrap", {})

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Quant Research Evaluation Report - {eval_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #0b0f19; color: #e2e8f0; margin: 30px; }}
        h1, h2, h3 {{ color: #38bdf8; }}
        .card {{ background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        .metric-grid {{ display: flex; gap: 20px; font-size: 18px; }}
        .metric-box {{ background: #0f172a; padding: 15px; border-radius: 6px; flex: 1; border-left: 4px solid #38bdf8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background-color: #0f172a; color: #94a3b8; }}
        .alert {{ background: #451a03; border-left: 4px solid #f97316; padding: 15px; margin-top: 20px; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>⚡ Quant AI Strategy Evaluation Report</h1>
    <div class="card">
        <h2>Executive Summary - {eval_id}</h2>
        <div class="metric-grid">
            <div class="metric-box">
                <small>CAGR</small><br><strong>{perf.get('cagr', 0.0):.2%}</strong>
            </div>
            <div class="metric-box">
                <small>Sharpe Ratio</small><br><strong>{perf.get('sharpe_ratio', 0.0):.2f}</strong>
            </div>
            <div class="metric-box">
                <small>Bootstrap Sharpe 95% CI</small><br><strong>[{boot.get('ci_lower', 0.0):.2f}, {boot.get('ci_upper', 0.0):.2f}]</strong>
            </div>
            <div class="metric-box">
                <small>Walk-Forward OOS Sharpe</small><br><strong>{wf.get('out_of_sample_sharpe', 0.0):.2f}</strong>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>Performance Ratios</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Return</td><td>{perf.get('total_return', 0.0):.2%}</td></tr>
            <tr><td>Annualized Volatility</td><td>{perf.get('annualized_volatility', 0.0):.2%}</td></tr>
            <tr><td>Sortino Ratio</td><td>{perf.get('sortino_ratio', 0.0):.2f}</td></tr>
            <tr><td>Maximum Drawdown</td><td>{perf.get('max_drawdown', 0.0):.2%}</td></tr>
            <tr><td>Calmar Ratio</td><td>{perf.get('calmar_ratio', 0.0):.2f}</td></tr>
            <tr><td>Win Rate</td><td>{perf.get('win_rate', 0.0):.1%}</td></tr>
        </table>
    </div>

    <div class="alert">
        <strong>Research Disclaimer:</strong> All results represent historical statistical evaluations. Past performance does not guarantee future results.
    </div>
</body>
</html>
"""
        return html
