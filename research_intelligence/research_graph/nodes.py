"""
Research Graph Node Definitions.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, Optional


class NodeType(str, Enum):
    HYPOTHESIS = "HYPOTHESIS"
    EXPERIMENT = "EXPERIMENT"
    DATASET = "DATASET"
    FEATURE = "FEATURE"
    MODEL = "MODEL"
    RESULT = "RESULT"
    VALIDATION = "VALIDATION"
    FINDING = "FINDING"


@dataclass
class ResearchNode:
    node_id: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["node_type"] = self.node_type.value
        return data
