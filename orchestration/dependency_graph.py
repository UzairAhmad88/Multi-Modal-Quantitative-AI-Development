"""
14-Stage Dependency Graph and Topological Sort DAG for Orchestration OS.
"""

from typing import Dict, List, Set


class PipelineDependencyGraph:
    """Manages stage dependencies and generates topological execution order."""

    def __init__(self):
        # Explicit 14-stage DAG dependencies
        self.dependencies: Dict[str, List[str]] = {
            "DATA": [],
            "FEATURES": ["DATA"],
            "VALIDATION": ["FEATURES"],
            "TRAINING": ["VALIDATION"],
            "PREDICTION": ["TRAINING"],
            "ALPHA": ["PREDICTION"],
            "PORTFOLIO": ["ALPHA"],
            "EXECUTION": ["PORTFOLIO"],
            "BACKTEST": ["EXECUTION"],
            "RISK": ["BACKTEST"],
            "STATISTICS": ["RISK"],
            "ROBUSTNESS": ["STATISTICS"],
            "MONITORING": ["ROBUSTNESS"],
            "REPORT": ["MONITORING"],
        }

    def get_prerequisites(self, stage_name: str) -> List[str]:
        return self.dependencies.get(stage_name, [])

    def get_execution_order(self) -> List[str]:
        """Returns topological sort of stage execution order."""
        ordered = []
        visited = set()

        def visit(node: str):
            if node not in visited:
                for dep in self.dependencies.get(node, []):
                    visit(dep)
                visited.add(node)
                ordered.append(node)

        for stage in self.dependencies.keys():
            visit(stage)

        return ordered
