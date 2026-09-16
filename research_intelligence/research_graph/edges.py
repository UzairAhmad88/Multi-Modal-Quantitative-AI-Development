"""
Research Graph Edge Definitions.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, Optional


class EdgeType(str, Enum):
    TESTED_BY = "tested_by"
    USES = "uses"
    PRODUCES = "produces"
    FEEDS = "feeds"
    EVALUATED_BY = "evaluated_by"
    SUPPORTS = "supports"


@dataclass
class ResearchEdge:
    source_id: str
    target_id: str
    edge_type: EdgeType
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["edge_type"] = self.edge_type.value
        return data
