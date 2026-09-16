"""
Experiment Report Generator: Compiles Markdown, HTML, and JSON reports for a research experiment.
"""

from typing import Dict, Any
import json


class ExperimentReportBuilder:
    """Generates structured research laboratory experiment reports."""

    def build_report(self, experiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates Markdown, HTML, and JSON report strings."""
        exp_id = experiment_data.get("experiment_id", "EXP-001")
        name = experiment_data.get("name", "Multimodal Experiment")
        hyp = experiment_data.get("hypothesis", {})
        metrics = experiment_data.get("metrics", {})
        runs = experiment_data.get("runs", [])
        lineage = experiment_data.get("lineage", {})

        md = f"""# Experiment Laboratory Report: {exp_id} ({name})

## 1. Experiment Overview & State
- **Status**: `{experiment_data.get('status', 'DRAFT')}`
- **Configuration Hash**: `{experiment_data.get('configuration_hash', 'N/A')}`
- **Dataset ID**: `{experiment_data.get('dataset_id', 'N/A')}`
- **Feature Version**: `{experiment_data.get('feature_version', 'N/A')}`
- **Model Version**: `{experiment_data.get('model_version', 'N/A')}`
- **Random Seed**: `{experiment_data.get('random_seed', 42)}`
- **Total Runs**: {len(runs)}

## 2. Research Hypothesis
- **Question**: {hyp.get('research_question', 'N/A')}
- **Hypothesis**: {hyp.get('hypothesis', 'N/A')}
- **Null Hypothesis**: {hyp.get('null_hypothesis', 'N/A')}
- **Success Criteria**: {hyp.get('success_criteria', 'N/A')}

## 3. Results Summary
| Metric | Value |
| :--- | :--- |
| **CAGR** | {metrics.get('cagr', 0.0):.2%} |
| **Sharpe Ratio** | {metrics.get('sharpe_ratio', 0.0):.2f} |
| **Sortino Ratio** | {metrics.get('sortino_ratio', 0.0):.2f} |
| **Max Drawdown** | {metrics.get('max_drawdown', 0.0):.2%} |

## 4. End-to-End Lineage DAG
`Dataset` → `Feature` → `Model` → `Signal` → `Portfolio` → `Execution` → `Backtest` → `Evaluation` → `Report`
"""

        html = f"<html><body><h1>Experiment {exp_id}</h1><p>Status: {experiment_data.get('status')}</p></body></html>"

        return {
            "experiment_id": exp_id,
            "markdown": md,
            "html": html,
            "json": json.dumps(experiment_data, indent=2)
        }
