"""
Priority Job Queue for Orchestrator Tasks.
"""

from typing import List, Optional
import heapq
from orchestrator.schemas.workflow_schema import Job
from orchestrator.core.states import Priority, JobStatus


class JobQueue:
    """
    Local Priority Queue ordering jobs by Priority (HIGH=1, NORMAL=2, LOW=3).
    """

    PRIORITY_MAP = {
        Priority.HIGH: 1,
        Priority.NORMAL: 2,
        Priority.LOW: 3,
    }

    def __init__(self):
        self._heap: List[tuple] = []
        self._counter = 0

    def push(self, job: Job):
        priority_val = self.PRIORITY_MAP.get(job.priority, 2)
        heapq.heappush(self._heap, (priority_val, self._counter, job))
        self._counter += 1

    def pop(self) -> Optional[Job]:
        if not self._heap:
            return None
        _, _, job = heapq.heappop(self._heap)
        return job

    def peek(self) -> Optional[Job]:
        if not self._heap:
            return None
        return self._heap[0][2]

    def size(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0
