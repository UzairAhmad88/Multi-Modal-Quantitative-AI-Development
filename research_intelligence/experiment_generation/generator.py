"""
Experiment Generator for Quantitative Research Intelligence.
Transforms structured ResearchHypothesis objects into executable experiment configuration files.
"""

from typing import Dict, Any, Optional
import yaml
from pathlib import Path

from research_intelligence.hypotheses.hypothesis_engine import ResearchHypothesis


class ExperimentGenerator:
    """Translates ResearchHypothesis instances into executable pipeline experiment YAML files."""

    def __init__(self, output_dir: str = "configs/experiments"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_experiment_config(
        self,
        hypothesis: ResearchHypothesis,
        symbols: Optional[list] = None,
        model_type: str = "multimodal",
        seed: int = 42
    ) -> Dict[str, Any]:
        """Builds pipeline experiment configuration dictionary."""
        config = {
            "experiment": {
                "name": f"exp_{hypothesis.hypothesis_id.lower().replace('-', '_')}",
                "hypothesis_id": hypothesis.hypothesis_id,
                "description": f"Automated experiment testing hypothesis: {hypothesis.statement}",
                "seed": seed
            },
            "data": {
                "symbols": symbols or ["AAPL", "MSFT", "GOOGL", "NVDA"],
                "start": "2020-01-01",
                "end": "2025-01-01"
            },
            "features": {
                "market": True,
                "news": hypothesis.independent_variable.startswith("news") or hypothesis.independent_variable == "sentiment",
                "fundamentals": "growth" in hypothesis.independent_variable or "fundamental" in hypothesis.independent_variable
            },
            "model": {
                "type": model_type,
                "version": "1.0"
            },
            "backtest": {
                "initial_capital": 100000.0,
                "transaction_cost": 0.001,
                "slippage": 0.0005
            },
            "validation": {
                "walk_forward": True,
                "leakage_detection": True,
                "bootstrap": True
            },
            "report": {
                "generate": True
            }
        }
        return config

    def save_experiment_yaml(
        self,
        hypothesis: ResearchHypothesis,
        config: Dict[str, Any]
    ) -> str:
        """Saves experiment configuration to YAML file."""
        filename = f"{hypothesis.hypothesis_id.lower().replace('-', '_')}.yaml"
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(config, f, sort_keys=False)
        return str(filepath)
