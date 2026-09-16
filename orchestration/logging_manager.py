"""
Logging Manager for Research Pipeline Runs.
Outputs structured JSON logs and saves run log files to logs/runs/<run_id>.log.
"""

import os
import json
import logging
import datetime
from typing import Dict, Any, Optional


class LoggingManager:
    """Manages structured JSON logging per run and stage."""

    def __init__(self, log_dir: str = "logs/runs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def log_event(
        self,
        run_id: str,
        stage: str,
        status: str,
        severity: str = "INFO",
        message: str = "",
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "run_id": run_id,
            "stage": stage,
            "status": status,
            "severity": severity,
            "message": message,
            "extra": extra or {},
        }

        log_file = os.path.join(self.log_dir, f"{run_id}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        return log_entry
