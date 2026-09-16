"""
Lineage Tracker Module
Constructs full research lineage DAGs tracing Result -> Run -> Model -> Feature -> Dataset -> Config -> Git Commit.
"""

from typing import Dict, List, Any, Optional


class LineageTracker:
    """Quantitative Research Lineage & Dependency Graph Engine."""

    def __init__(self):
        self.graphs: Dict[str, Dict[str, Any]] = {}

    def record_node(self, run_id: str, node_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Record an individual lineage node for a run."""
        if run_id not in self.graphs:
            self.graphs[run_id] = {"run_id": run_id, "nodes": {}, "edges": []}
        
        self.graphs[run_id]["nodes"][node_type] = data
        self.graphs[run_id]["edges"].append(f"RUN -> {node_type.upper()}")
        return self.graphs[run_id]

    def build_lineage_graph(
        self,
        run_id: str,
        model_version: str = "v1.0.0",
        feature_version: str = "v1.0.0",
        dataset_version: str = "v1.0.0",
        strategy_version: str = "v1.0.0",
        git_commit: str = "HEAD",
        config_path: str = "configs/experiments/multimodal.yaml",
    ) -> Dict[str, Any]:
        """
        Build and record end-to-end lineage dependency node graph.
        """
        graph = {
            "run_id": run_id,
            "nodes": {
                "result": {"node_type": "RESULT", "run_id": run_id},
                "strategy": {"node_type": "STRATEGY_VERSION", "version": strategy_version},
                "model": {"node_type": "MODEL_VERSION", "version": model_version},
                "feature": {"node_type": "FEATURE_VERSION", "version": feature_version},
                "dataset": {"node_type": "DATASET_VERSION", "version": dataset_version},
                "config": {"node_type": "CONFIG", "path": config_path},
                "code": {"node_type": "GIT_COMMIT", "commit": git_commit},
            },
            "edges": [
                "RESULT -> RUN",
                "RUN -> STRATEGY_VERSION",
                "STRATEGY_VERSION -> MODEL_VERSION",
                "MODEL_VERSION -> FEATURE_VERSION",
                "FEATURE_VERSION -> DATASET_VERSION",
                "MODEL_VERSION -> CONFIG",
                "CONFIG -> GIT_COMMIT",
            ],
        }
        self.graphs[run_id] = graph
        return graph

    def get_lineage(self, run_id: str) -> Dict[str, Any]:
        """Retrieve lineage graph for a run_id."""
        if run_id in self.graphs:
            return self.graphs[run_id]
        return self.build_lineage_graph(run_id)
