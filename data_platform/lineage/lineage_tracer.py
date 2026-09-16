"""
Data & Feature Lineage Tracer for Dataset Dependency Graph Visualizations.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import datetime


class DataLineageTracer:
    """Tracks end-to-end lineage mapping from Raw Source -> Features -> Dataset -> Model."""

    def __init__(self, lineage_file: str = "artifacts/data_platform_lineage.json"):
        self.lineage_path = Path(lineage_file)
        self.lineage_path.parent.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.lineage_path.exists():
            try:
                with open(self.lineage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"nodes": {}, "edges": []}

    def _save(self) -> None:
        with open(self.lineage_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def record_node(self, node_id: str, node_type: str, metadata: Dict[str, Any]) -> None:
        self._data["nodes"][node_id] = {
            "id": node_id,
            "type": node_type,
            "metadata": metadata,
            "recorded_at": datetime.datetime.utcnow().isoformat()
        }
        self._save()

    def record_edge(self, parent_id: str, child_id: str, relation: str) -> None:
        edge = {"parent": parent_id, "child": child_id, "relation": relation}
        if edge not in self._data["edges"]:
            self._data["edges"].append(edge)
            self._save()

    def get_lineage(self, node_id: str) -> Dict[str, Any]:
        """Returns upstream parents and downstream children for a given node."""
        parents = [e["parent"] for e in self._data["edges"] if e["child"] == node_id]
        children = [e["child"] for e in self._data["edges"] if e["parent"] == node_id]
        return {
            "node": self._data["nodes"].get(node_id),
            "parents": [self._data["nodes"].get(p) for p in parents if p in self._data["nodes"]],
            "children": [self._data["nodes"].get(c) for c in children if c in self._data["nodes"]]
        }
