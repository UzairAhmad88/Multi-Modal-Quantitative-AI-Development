"""
Research Knowledge Graph Engine.
"""

from typing import Dict, Any, List, Set, Tuple
from knowledge.schemas.knowledge_record import ResearchKnowledgeRecord


class ResearchKnowledgeGraph:
    """
    Constructs and queries an interactive knowledge graph of Datasets, Features, Models, Experiments, Backtests, Claims, and Reports.
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []

    def add_node(self, node_id: str, node_type: str, label: str, metadata: Dict[str, Any] = None):
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "metadata": metadata or {},
        }

    def add_edge(self, source: str, target: str, relation: str):
        self.edges.append({"source": source, "target": target, "relation": relation})

    def build_from_records(self, records: List[ResearchKnowledgeRecord]):
        for rec in records:
            # Nodes
            self.add_node(rec.dataset_id, "Dataset", f"Dataset: {rec.dataset_id}")
            self.add_node(rec.feature_set_id, "FeatureSet", f"Features: {rec.feature_set_id}")
            self.add_node(rec.model_id, "Model", f"Model: {rec.model_id}")
            self.add_node(rec.experiment_id, "Experiment", f"Exp: {rec.experiment_id}")
            if rec.report_id:
                self.add_node(rec.report_id, "Report", f"Report: {rec.report_id}")

            # Edges
            self.add_edge(rec.dataset_id, rec.feature_set_id, "GENERATES_FEATURES")
            self.add_edge(rec.feature_set_id, rec.model_id, "TRAINS")
            self.add_edge(rec.model_id, rec.experiment_id, "TESTED_IN")
            if rec.report_id:
                self.add_edge(rec.experiment_id, rec.report_id, "COMPILED_IN")

    def query_by_node(self, node_id: str) -> Dict[str, Any]:
        related_edges = [e for e in self.edges if e["source"] == node_id or e["target"] == node_id]
        related_node_ids = set()
        for e in related_edges:
            related_node_ids.add(e["source"])
            related_node_ids.add(e["target"])

        return {
            "queried_node": self.nodes.get(node_id),
            "connected_nodes": [self.nodes[nid] for nid in related_node_ids if nid in self.nodes],
            "edges": related_edges,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "nodes_count": len(self.nodes),
            "edges_count": len(self.edges),
        }
