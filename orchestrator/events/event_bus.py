"""
Event bus and JSONL event store for Phase 22 Orchestrator.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional


class EventBus:
    """
    Stores and emits structured workflow events to logs/workflows/<workflow_id>/events.jsonl.
    """

    def __init__(self, base_dir: str = "logs/workflows"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_event_file(self, workflow_id: str) -> str:
        wf_dir = os.path.join(self.base_dir, workflow_id)
        os.makedirs(wf_dir, exist_ok=True)
        return os.path.join(wf_dir, "events.jsonl")

    def emit(
        self,
        event_type: str,
        workflow_id: str,
        task_id: Optional[str] = None,
        experiment_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        event_record = {
            "event_id": f"EVT-{uuid.uuid4().hex[:8]}",
            "workflow_id": workflow_id,
            "task_id": task_id,
            "experiment_id": experiment_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload or {},
        }
        event_file = self._get_event_file(workflow_id)
        with open(event_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_record) + "\n")
        return event_record

    def get_events(self, workflow_id: str) -> List[Dict[str, Any]]:
        event_file = self._get_event_file(workflow_id)
        if not os.path.exists(event_file):
            return []
        events = []
        with open(event_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line.strip()))
        return events
