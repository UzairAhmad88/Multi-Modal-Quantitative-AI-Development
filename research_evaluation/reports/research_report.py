"""
Research Report Generator: Compiles Markdown and JSON research report.
"""

from typing import Dict, Any, List
import json


class ResearchReportGenerator:
    """Generates structured Markdown research reports."""

    def generate_markdown_report(self, evaluation_result: Dict[str, Any]) -> str:
        """Builds comprehensive research report text."""
        eval_id = evaluation_result.get("evaluation_id", "EVAL-001")
        perf = evaluation_result.get("performance", {})
        wf = evaluation_result.get("walk_forward", {})
        boot = evaluation_result.get("bootstrap", {})
        overfit = evaluation_result.get("overfitting", {})

        md = f"""# Quantitative Research Evaluation Report: {eval_id}

## 1. Executive Summary
- **Strategy ID**: {evaluation_result.get('strategy_id', 'STRATEGY-001')}
- **CAGR**: {perf.get('cagr', 0.0):.2%}
- **Sharpe Ratio**: {perf.get('sharpe_ratio', 0.0):.2f} (95% CI: [{boot.get('ci_lower', 0.0):.2f}, {boot.get('ci_upper', 0.0):.2f}])
- **Max Drawdown**: {perf.get('max_drawdown', 0.0):.2%}
- **Out-of-Sample Walk-Forward Sharpe**: {wf.get('out_of_sample_sharpe', 0.0):.2f}
- **Overfitting Risk Level**: {overfit.get('overfitting_risk_level', 'UNKNOWN')}

## 2. Performance & Risk Ratios
| Metric | Value |
| :--- | :--- |
| **Total Return** | {perf.get('total_return', 0.0):.2%} |
| **CAGR** | {perf.get('cagr', 0.0):.2%} |
| **Annualized Volatility** | {perf.get('annualized_volatility', 0.0):.2%} |
| **Sharpe Ratio** | {perf.get('sharpe_ratio', 0.0):.2f} |
| **Sortino Ratio** | {perf.get('sortino_ratio', 0.0):.2f} |
| **Calmar Ratio** | {perf.get('calmar_ratio', 0.0):.2f} |
| **Win Rate** | {perf.get('win_rate', 0.0):.1%} |
| **Profit Factor** | {perf.get('profit_factor', 0.0):.2f} |

## 3. Statistical Validation & Out-Of-Sample Testing
- **Significance t-stat**: {evaluation_result.get('significance', {}).get('t_statistic', 0.0)} (p-value: {evaluation_result.get('significance', {}).get('p_value_one_tailed', 1.0):.4f})
- **Permutation Test p-value**: {evaluation_result.get('permutation', {}).get('permutation_p_value', 1.0):.4f}
- **Stationarity ADF Test**: {'PASS' if evaluation_result.get('stationarity', {}).get('is_stationary') else 'FAIL'}
- **Leakage Detection**: {'CLEAN' if evaluation_result.get('leakage', {}).get('clean') else 'VIOLATION DETECTED'}

## 4. Research Limitations & Disclaimer
> [!WARNING]
> Historical out-of-sample simulation results do not guarantee future investment performance. All evaluations are for quantitative research purposes only.
"""
        return md
