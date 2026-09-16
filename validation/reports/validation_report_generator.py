"""
Validation Report Generator for Markdown & JSON Output.
"""

import os
from typing import Dict, Any
from validation.schemas.validation_schema import StatisticalValidation


class ValidationReportGenerator:
    """
    Generates technical Markdown validation reports from StatisticalValidation instances.
    """

    @staticmethod
    def generate_report_md(val: StatisticalValidation) -> str:
        md = f"""# Statistical Validation & Research Integrity Report

## Metadata
- **Validation ID**: `{val.validation_id}`
- **Experiment ID**: `{val.experiment_id}`
- **Status**: `{val.validation_status}`
- **Configuration Hash**: `{val.configuration_hash}`
- **Sample Size**: `{val.sample_size}` observations
- **Created At**: `{val.created_at}`

## Basic Statistics & Parametric Confidence Interval
- **Mean Return**: `{val.basic_statistics.get('mean', 0.0)}`
- **Standard Deviation**: `{val.basic_statistics.get('std', 0.0)}`
- **Skewness**: `{val.basic_statistics.get('skewness', 0.0)}`
- **Kurtosis**: `{val.basic_statistics.get('kurtosis', 0.0)}`
- **Parametric 95% CI**: `[{val.confidence_intervals.get('lower_bound', 0.0)}, {val.confidence_intervals.get('upper_bound', 0.0)}]`

## Stationary Block Bootstrap Analysis
"""
        for boot in val.bootstrap_results:
            md += f"- **Metric**: `{boot.metric}` | **Estimate**: `{boot.estimate}` | **95% Bootstrap CI**: `[{boot.lower_bound}, {boot.upper_bound}]` (Iterations: `{boot.iterations}`, Block Size: `{boot.block_size}`)\n"

        md += "\n## Hypothesis Testing & Significance\n"
        for sig in val.significance_results:
            md += f"- **Test**: `{sig.test_name}` | **p-value**: `{sig.p_value}` | **t-stat**: `{sig.test_statistic}` | **Cohen's d**: `{sig.effect_size}` | **Significant (<0.05)**: `{'YES' if sig.is_statistically_significant else 'NO'}`\n"

        if val.multiple_testing_result:
            mt = val.multiple_testing_result
            md += f"\n## Multiple Testing Correction (`{mt.method}`)\n"
            md += f"- **Number of Tests**: `{mt.number_of_tests}`\n"
            md += f"- **Adjusted p-values**: `{mt.adjusted_p_values}`\n"

        if val.stability_result:
            st_res = val.stability_result
            md += f"\n## Temporal Stability Analysis\n"
            md += f"- **Stability Score**: `{st_res.stability_score} / 100` | **Sharpe Std**: `{st_res.sharpe_std}` | **Drawdown Std**: `{st_res.drawdown_std}`\n"

        if val.integrity_flags:
            md += "\n## Research Integrity Flags\n"
            for flag in val.integrity_flags:
                md += f"- [{flag.severity}] **{flag.flag_type}**: {flag.message}\n"

        md += "\n## Assumptions & Limitations\n"
        md += "- Results are based on historical return series under explicit statistical assumptions.\n"
        md += "- Statistical significance does not constitute a recommendation or guarantee of future performance.\n"

        out_dir = "reports/validation"
        os.makedirs(out_dir, exist_ok=True)
        filepath = os.path.join(out_dir, f"val_{val.validation_id}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        return md
