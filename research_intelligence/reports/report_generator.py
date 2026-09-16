"""
Research Intelligence Report Generator.
Compiles structured quantitative research reports adhering to standard academic markdown format.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import datetime


class ResearchIntelligenceReportGenerator:
    """Generates structured research intelligence Markdown reports under reports/research_intelligence/."""

    def __init__(self, output_dir: str = "reports/research_intelligence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        experiment_id: str,
        hypothesis: Dict[str, Any],
        patterns: List[Dict[str, Any]],
        evidence: Dict[str, Any],
        questions: List[str]
    ) -> str:
        """Generates comprehensive Markdown report."""
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        filepath = self.output_dir / f"{experiment_id}_report.md"

        content = f"""# Quantitative Research Intelligence Report — {experiment_id}

**Generated**: {timestamp}  
**Hypothesis ID**: {hypothesis.get('hypothesis_id', 'N/A')}  
**Evidence Status**: `{evidence.get('status', 'N/A')}`

---

## 1. Research Question & Hypothesis
- **Statement**: {hypothesis.get('statement', 'N/A')}
- **Independent Variable**: `{hypothesis.get('independent_variable', 'N/A')}`
- **Dependent Variable**: `{hypothesis.get('dependent_variable', 'N/A')}`
- **Null Hypothesis ($H_0$)**: {hypothesis.get('null_hypothesis', 'N/A')}
- **Alternative Hypothesis ($H_1$)**: {hypothesis.get('alternative_hypothesis', 'N/A')}

---

## 2. Data & Methodology
- **Asset Population**: {hypothesis.get('population', 'SP500')}
- **Time Horizon**: $t + {hypothesis.get('time_horizon', 1)}$
- **Testing Method**: {hypothesis.get('test_method', 'Walk-Forward Simulation')}

---

## 3. Discovered Patterns & Evidence
"""
        for p in patterns:
            content += f"- **{p.get('pattern_name', 'Pattern')}** ({p.get('category', 'GENERAL')}): {p.get('description', '')}\n"

        content += f"""
---

## 4. Empirical Evaluation & Metrics
- **Sharpe Ratio**: `{evidence.get('sharpe_ratio', 'N/A')}`
- **CAGR**: `{evidence.get('cagr', 'N/A')}`
- **Max Drawdown**: `{evidence.get('max_drawdown', 'N/A')}`
- **Statistical Significance ($p$-value)**: `{evidence.get('p_value', 'N/A')}`
- **Sample Size ($N$)**: `{evidence.get('sample_size', 'N/A')}`

**Summary**: {evidence.get('summary', '')}

---

## 5. Limitations & Caveats
"""
        for lim in evidence.get("limitations", []):
            content += f"- {lim}\n"

        content += """
---

## 6. Open Research Questions
"""
        for q in questions:
            content += f"- {q}\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return str(filepath)
