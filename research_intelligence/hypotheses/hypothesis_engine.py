"""
Hypothesis Engine for Quantitative Research Intelligence.
Generates, validates, and stores structured hypotheses with explicit null and alternative hypotheses.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import datetime
import uuid
import yaml
from pathlib import Path

from research_intelligence.hypotheses.hypothesis_types import HypothesisType


@dataclass
class ResearchHypothesis:
    hypothesis_id: str
    statement: str
    hypothesis_type: HypothesisType
    independent_variable: str
    dependent_variable: str
    null_hypothesis: str
    alternative_hypothesis: str
    test_method: str
    time_horizon: int = 1
    population: str = "SP500"
    limitations: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    status: str = "DRAFT"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["hypothesis_type"] = self.hypothesis_type.value
        return data

    def to_yaml(self) -> str:
        return yaml.dump({"hypothesis": self.to_dict()}, sort_keys=False)


class HypothesisEngine:
    """Generates testable research hypotheses from discovered patterns and anomalies."""

    def __init__(self, storage_dir: str = "artifacts/hypotheses"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_hypothesis(
        self,
        statement: str,
        hypothesis_type: HypothesisType,
        independent_variable: str,
        dependent_variable: str,
        null_hypothesis: str,
        alternative_hypothesis: str,
        test_method: str = "Linear Regression / Correlation Test",
        time_horizon: int = 1,
        population: str = "SP500",
        limitations: Optional[List[str]] = None
    ) -> ResearchHypothesis:
        """Constructs a structured testable ResearchHypothesis."""
        hyp_id = f"HYP-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        # Guarantee strict falsifiability
        if not null_hypothesis:
            null_hypothesis = f"No measurable relationship between {independent_variable} and {dependent_variable}."
        if not alternative_hypothesis:
            alternative_hypothesis = f"A statistically significant relationship exists between {independent_variable} and {dependent_variable}."

        hyp = ResearchHypothesis(
            hypothesis_id=hyp_id,
            statement=statement,
            hypothesis_type=hypothesis_type,
            independent_variable=independent_variable,
            dependent_variable=dependent_variable,
            null_hypothesis=null_hypothesis,
            alternative_hypothesis=alternative_hypothesis,
            test_method=test_method,
            time_horizon=time_horizon,
            population=population,
            limitations=limitations or ["Assumes historical pattern stability", "Subject to transaction costs and market regimes"]
        )

        self.save_hypothesis(hyp)
        return hyp

    def save_hypothesis(self, hypothesis: ResearchHypothesis) -> str:
        filepath = self.storage_dir / f"{hypothesis.hypothesis_id}.yaml"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(hypothesis.to_yaml())
        return str(filepath)

    def get_hypothesis(self, hypothesis_id: str) -> Optional[ResearchHypothesis]:
        filepath = self.storage_dir / f"{hypothesis_id}.yaml"
        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f).get("hypothesis", {})
            return ResearchHypothesis(
                hypothesis_id=data["hypothesis_id"],
                statement=data["statement"],
                hypothesis_type=HypothesisType(data["hypothesis_type"]),
                independent_variable=data["independent_variable"],
                dependent_variable=data["dependent_variable"],
                null_hypothesis=data["null_hypothesis"],
                alternative_hypothesis=data["alternative_hypothesis"],
                test_method=data["test_method"],
                time_horizon=data.get("time_horizon", 1),
                population=data.get("population", "SP500"),
                limitations=data.get("limitations", []),
                created_at=data.get("created_at", ""),
                status=data.get("status", "DRAFT")
            )
        except Exception:
            return None

    def list_hypotheses(self) -> List[ResearchHypothesis]:
        results = []
        for file in self.storage_dir.glob("HYP-*.yaml"):
            hyp = self.get_hypothesis(file.stem)
            if hyp:
                results.append(hyp)
        return results

    def generate_hypotheses_from_patterns(self, pattern_results: Dict[str, Any]) -> List[ResearchHypothesis]:
        """Auto-generates structured hypotheses from pattern discovery findings."""
        generated = []
        patterns = pattern_results.get("patterns", [])

        for pat in patterns:
            p_name = pat.get("pattern_name", "Pattern")
            desc = pat.get("description", "")
            cat = pat.get("category", "CROSS_MODAL")

            if cat == "CROSS_MODAL":
                parts = p_name.split(" vs ")
                indep = parts[0] if len(parts) > 1 else "news_sentiment"
                dep = parts[1] if len(parts) > 1 else "returns"
            else:
                indep = "volatility" if "vol" in p_name.lower() else "news_sentiment"
                dep = "returns"

            hyp = self.create_hypothesis(
                statement=f"{indep} has a predictive relationship with {dep} ({desc}).",
                hypothesis_type=HypothesisType.MULTIMODAL if cat == "CROSS_MODAL" else HypothesisType.CORRELATIONAL,
                independent_variable=indep,
                dependent_variable=dep,
                null_hypothesis=f"No predictive relationship exists between {indep} and {dep}.",
                alternative_hypothesis=f"A statistically significant predictive relationship exists between {indep} and {dep}.",
                test_method="Walk-forward backtest & t-statistic significance test",
                time_horizon=1
            )
            generated.append(hyp)

        return generated
