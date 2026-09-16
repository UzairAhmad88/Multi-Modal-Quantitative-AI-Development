"""
Markdown Report Generators for Research Knowledge Base.
"""

import os
from typing import Dict, Any, List
from knowledge.schemas.knowledge_record import ResearchKnowledgeRecord, ReproducibilityCard


class KnowledgeReportGenerator:
    """
    Generates Markdown reports for experiment summaries, comparison reports, and reproducibility cards.
    """

    @staticmethod
    def generate_reproducibility_card_md(card: ReproducibilityCard) -> str:
        md = f"""# Reproducibility Card: {card.experiment_id} ({card.card_id})

## Execution Metadata
- **Code Version**: `{card.code_version}`
- **Random Seed**: `{card.random_seed}`
- **Configuration Hash**: `{card.configuration_hash}`
- **Execution Timestamp**: `{card.execution_timestamp}`

## Version Lineage
- **Dataset ID**: `{card.dataset_id}` (Version: `{card.dataset_version}`)
- **Feature Version**: `{card.feature_version}`
- **Model Version**: `{card.model_version}`

## Environment Details
"""
        for k, v in card.environment_info.items():
            md += f"- **{k}**: `{v}`\n"

        md += "\n## Artifact Locations\n"
        for k, v in card.artifact_locations.items():
            md += f"- **{k}**: `{v}`\n"

        out_dir = "reports/knowledge"
        os.makedirs(out_dir, exist_ok=True)
        filepath = os.path.join(out_dir, f"card_{card.experiment_id}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        return md

    @staticmethod
    def generate_comparison_report_md(comp_result: Dict[str, Any]) -> str:
        exp_a = comp_result["experiment_a"]
        exp_b = comp_result["experiment_b"]
        is_fair = comp_result["is_fair_comparison"]

        md = f"""# Experiment Comparison Report: {exp_a} vs {exp_b}

## Comparability Status
- **Fair Comparison**: `{"YES" if is_fair else "NO (WARNINGS RAISED)"}`
"""
        if comp_result.get("warnings"):
            md += "### Warnings:\n"
            for w in comp_result["warnings"]:
                md += f"- ⚠️ {w}\n"

        md += "\n## Metrics Comparison Table\n\n"
        md += "| Metric | Experiment A | Experiment B | Delta | % Change |\n"
        md += "|--------|--------------|--------------|-------|----------|\n"

        for row in comp_result.get("metrics_comparison", []):
            m = row["metric"]
            va = row["experiment_a"]
            vb = row["experiment_b"]
            d = row["delta"] if row["delta"] is not None else "-"
            pc = f"{row['percent_change']}%" if row["percent_change"] is not None else "-"
            md += f"| `{m}` | {va} | {vb} | {d} | {pc} |\n"

        md += "\n## Evidence & Provenance Notes\n"
        md += "- Deltas represent empirical observations across historical backtest runs.\n"
        md += "- Causality cannot be inferred without controlled ablation testing.\n"

        out_dir = "reports/knowledge"
        os.makedirs(out_dir, exist_ok=True)
        filepath = os.path.join(out_dir, f"comp_{exp_a}_vs_{exp_b}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        return md
