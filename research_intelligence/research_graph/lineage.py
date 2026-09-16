"""
Lineage Queries for Research Graph Traceability.
Traces full lineage chains for findings, models, and datasets.
"""

from typing import Dict, Any, List, Optional
from research_intelligence.research_graph.nodes import ResearchNode, NodeType
from research_intelligence.research_graph.edges import ResearchEdge, EdgeType


class LineageQueryEngine:
    """Executes lineage queries on ResearchGraph."""

    def __init__(self, nodes: Dict[str, ResearchNode], edges: List[ResearchEdge]):
        self.nodes = nodes
        self.edges = edges

    def trace_finding_lineage(self, finding_id: str) -> Dict[str, Any]:
        """Traces finding -> hypothesis -> experiment -> dataset -> model -> validation lineage chain."""
        chain = []
        curr = finding_id

        visited = set()
        while curr and curr not in visited:
            visited.add(curr)
            node = self.nodes.get(curr)
            if node:
                chain.append(node.to_dict())

            # Find incoming edges where target_id == curr
            incoming = [e for e in self.edges if e.target_id == curr]
            if incoming:
                curr = incoming[0].source_id
            else:
                curr = None

        return {
            "finding_id": finding_id,
            "lineage_depth": len(chain),
            "lineage_chain": chain
        }
