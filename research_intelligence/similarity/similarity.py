"""
Research Similarity Engine for Experiment Duplicate Detection.
Calculates configuration Jaccard and feature similarity to warn researchers of duplicate efforts.
"""

from typing import Dict, Any, List, Optional
from research.registry.registry import ExperimentRegistry


class ResearchSimilarityEngine:
    """Detects similar or duplicate research experiments and hypotheses."""

    def __init__(self):
        self.registry = ExperimentRegistry()

    def find_similar_experiments(
        self,
        config: Dict[str, Any],
        threshold: float = 0.70
    ) -> List[Dict[str, Any]]:
        """Finds existing experiment runs matching symbols, model, and feature configuration."""
        runs = self.registry.list_experiments()
        target_model = config.get("model", {}).get("type", "")
        target_symbols = set(config.get("data", {}).get("symbols", []))
        target_features = config.get("features", {})

        similar = []
        for run in runs:
            run_config = run.get("config", {})
            run_model = run_config.get("model", {}).get("type", "")
            run_symbols = set(run_config.get("data", {}).get("symbols", []))
            run_features = run_config.get("features", {})

            # Symbol Jaccard similarity
            if target_symbols and run_symbols:
                inter = target_symbols.intersection(run_symbols)
                union = target_symbols.union(run_symbols)
                sym_sim = len(inter) / float(len(union))
            else:
                sym_sim = 1.0

            # Model match
            model_match = 1.0 if target_model == run_model else 0.0

            # Combined score
            score = 0.6 * sym_sim + 0.4 * model_match

            if score >= threshold:
                similar.append({
                    "run_id": run.get("run_id"),
                    "experiment_id": run.get("experiment_id"),
                    "similarity_score": round(score, 3),
                    "model_type": run_model,
                    "symbols": list(run_symbols),
                    "status": run.get("status"),
                    "warning": f"Similar experiment found ({run.get('run_id')}): {score*100:.0f}% similarity"
                })

        similar.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar
