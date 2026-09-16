"""
DAG Validator & Topological Sort for Workflow Task Dependencies.
"""

from typing import List, Dict, Set, Tuple
from orchestrator.schemas.workflow_schema import WorkflowTask


class DAGValidationError(Exception):
    pass


class DAGValidator:
    """
    Validates DAG task graphs for workflow execution:
    - Detects cycles
    - Checks for missing task dependencies
    - Produces a valid topological execution order
    """

    @staticmethod
    def validate_and_sort(tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        task_map: Dict[str, WorkflowTask] = {t.task_id: t for t in tasks}
        
        # 1. Check for missing dependencies
        for t in tasks:
            for dep in t.depends_on:
                if dep not in task_map:
                    raise DAGValidationError(f"Task '{t.task_id}' depends on missing task '{dep}'")

        # 2. Build adjacency list and in-degrees
        adj: Dict[str, List[str]] = {t.task_id: [] for t in tasks}
        in_degree: Dict[str, int] = {t.task_id: 0 for t in tasks}

        for t in tasks:
            for dep in t.depends_on:
                adj[dep].append(t.task_id)
                in_degree[t.task_id] += 1

        # 3. Kahn's Algorithm for Topological Sort & Cycle Detection
        queue = [t_id for t_id, deg in in_degree.items() if deg == 0]
        sorted_ids: List[str] = []

        while queue:
            curr = queue.pop(0)
            sorted_ids.append(curr)

            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_ids) != len(tasks):
            raise DAGValidationError("Cyclic dependency detected in workflow task graph")

        return [task_map[t_id] for t_id in sorted_ids]
