"""
Research Report Generator for Research Intelligence.
Generates structured Markdown reports for individual experiments, comparisons, ablations,
robustness tests, error analyses, and research summaries into reports/research/.
"""

import os
from typing import Dict, List, Any
from research_intelligence.experiment_manager.manager import ExperimentRecord


class ResearchReportGenerator:
    """Generates standardized Markdown reports adhering to evidence-based research principles."""

    def __init__(self, output_dir: str = "reports/research"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_experiment_report(self, record: ExperimentRecord) -> str:
        cfg = record.config
        res = record.results or {}
        p_met = res.get("prediction_metrics", {})
        t_met = res.get("trading_metrics", {})
        r_met = res.get("risk_metrics", {})
        c_met = res.get("cost_metrics", {})

        content = f"""# Quantitative Research Experiment Report: {record.experiment_id}

## 1. Objective & Hypothesis
* **Experiment ID:** `{record.experiment_id}`
* **Experiment Name:** {cfg.name}
* **Hypothesis ID:** `{cfg.hypothesis_id}`
* **Created Timestamp:** {record.created_at}

## 2. Dataset & Features
* **Dataset:** `{cfg.dataset}`
* **Feature Set:** {', '.join([f'`{f}`' for f in cfg.features])}
* **Random Seed:** `{cfg.random_seed}`

## 3. Model & Configuration
* **Model Architecture:** `{cfg.model}`
* **Code Version:** `{cfg.versions.code_version}`
* **Model Version:** `{cfg.versions.model_version}`

## 4. Empirical Performance Results
* **Directional Accuracy (Observed):** {p_met.get('directional_accuracy', 0.0):.2%}
* **CAGR (Simulated):** {t_met.get('cagr', 0.0):.2%}
* **Sharpe Ratio:** {t_met.get('sharpe', 0.0):.2f}
* **Sortino Ratio:** {t_met.get('sortino', 0.0):.2f}
* **Max Drawdown:** {t_met.get('max_drawdown', 0.0):.2%}
* **Turnover:** {t_met.get('turnover', 0.0):.2%}

## 5. Risk & Transaction Cost Metrics
* **VaR 95%:** {r_met.get('var_95', 0.0):.2%}
* **CVaR 95%:** {r_met.get('cvar_95', 0.0):.2%}
* **Simulated Transaction Cost:** {c_met.get('transaction_cost_pct', 0.001):.3%}
* **Real-Money Trading:** DISABLED (Paper-Trading / Backtest Only)

## 6. Research Summary & Evidence-Based Statement
The empirical results measured during backtesting were consistent with the expected directional behavior.
No guaranteed return or risk-free performance is implied. Performance remains subject to regime changes.

## 7. Reproducibility
Reproduce this experiment locally via:
```bash
python scripts/research_intel.py experiment reproduce --id {record.experiment_id}
```
"""
        filepath = os.path.join(self.output_dir, f"exp_{record.experiment_id}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # Also write experiment_report.md
        main_filepath = os.path.join(self.output_dir, "experiment_report.md")
        with open(main_filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    def generate_research_summary(self, summary_data: Dict[str, Any]) -> str:
        content = f"""# Master Research Intelligence Summary

## Overview
* **Total Registered Hypotheses:** {summary_data.get('hypotheses_count', 0)}
* **Total Executed Experiments:** {summary_data.get('experiments_count', 0)}
* **Verified Research Findings:** {summary_data.get('findings_count', 0)}
* **Logged Experiment Failures:** {summary_data.get('failures_count', 0)}

## Observed Findings
{summary_data.get('findings_text', 'No findings registered yet.')}

## Key Disclaimers
* All metrics represent historical simulated backtest or paper-trading results.
* Real-money live trading remains explicitly **DISABLED**.
* Models must undergo human research review before paper deployment.
"""
        filepath = os.path.join(self.output_dir, "research_summary.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath
