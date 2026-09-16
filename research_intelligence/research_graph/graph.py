"""
Master Research Graph Network Implementation.
Stores nodes and edges representing quantitative research relationships and lineage.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path

from research_intelligence.research_graph.nodes import ResearchNode, NodeType
from research_intelligence.research_graph.edges import ResearchEdge, EdgeType
from research_intelligence.research_graph.lineage import LineageQueryEngine


class ResearchGraph:
    """Network graph representing Hypotheses, Experiments, Datasets, Models, and Findings."""

    def __init__(self, storage_file: str = "artifacts/research_graph.json"):
        self.storage_path = Path(storage_file)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.nodes: Dict[str, ResearchNode] = {}
        self.edges: List[ResearchEdge] = []
        self._load()

    def add_node(self, node_id: str, node_type: NodeType, label: str, properties: Optional[Dict[str, Any]] = None) -> ResearchNode:
        node = ResearchNode(node_id=node_id, node_type=node_type, label=label, properties=properties or {})
        self.nodes[node_id] = node
        self._save()
        return node

    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType, metadata: Optional[Dict[str, Any]] = None) -> ResearchEdge:
        edge = ResearchEdge(source_id=source_id, target_id=target_id, edge_type=edge_type, metadata=metadata or {})
        self.edges.append(edge)
        self._save()
        return edge

    def trace_lineage(self, finding_id: str) -> Dict[str, Any]:
        lqe = LineageQueryEngine(self.nodes, self.edges)
        return lqe.trace_finding_lineage(finding_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }

    def _save(self) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for n in data.get("nodes", []):
                node = ResearchNode(
                    node_id=n["node_id"],
                    node_type=NodeType(n["node_type"]),
                    label=n["label"],
                    properties=n.get("properties", {})
                )
                self.nodes[node.node_id] = node
            for e in data.get("edges", []):
                edge = ResearchEdge(
                    source_id=e["source_id"],
                    target_id=e["target_id"],
                    edge_type=EdgeType(e["edge_type"]),
                    metadata=e.get("metadata", {})
                )
                self.edges.append(edge)
        except Exception:
            pass
