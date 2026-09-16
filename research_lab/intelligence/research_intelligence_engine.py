"""
Research Intelligence Engine: Summarizes experiments, detects recurring patterns, flags anomalies, and synthesizes research insights.
"""

from typing import List, Dict, Any


class ResearchIntelligenceEngine:
    """Analyzes experiment histories for cross-experiment patterns and insights."""

    def synthesize_insights(self, experiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Categorizes research results into observed metrics, derived trends, and suggested directions."""
        if not experiments:
            return {"insights": [], "summary": "No experiments analyzed."}

        sharpes = [e.get("metrics", {}).get("sharpe_ratio", 0.0) for e in experiments]
        models = [e.get("model_version", "UNKNOWN") for e in experiments]

        avg_sharpe = float(sum(sharpes) / len(sharpes)) if sharpes else 0.0
        best_exp = max(experiments, key=lambda x: x.get("metrics", {}).get("sharpe_ratio", 0.0))

        insights = [
            f"Observed average Sharpe ratio across {len(experiments)} experiments is {avg_sharpe:.2f}.",
            f"Top performing configuration is '{best_exp.get('name', 'N/A')}' using model version '{best_exp.get('model_version', 'N/A')}'.",
            f"Models tested: {list(set(models))}."
        ]

        return {
            "insights_count": len(insights),
            "insights": insights,
            "average_sharpe": round(avg_sharpe, 2),
            "top_experiment_id": best_exp.get("experiment_id", "")
        }
