"""
Research Scheduler for Scheduled Pipelines and Data Updates.
Manages cron/interval scheduled tasks for data updates, validation runs, and reports.
"""

from typing import Dict, List, Any
import datetime


class ResearchScheduler:
    """Manages scheduled research tasks."""

    def __init__(self):
        self._schedules: List[Dict[str, Any]] = [
            {"task": "DAILY_DATA_UPDATE", "schedule": "0 0 * * *", "enabled": True},
            {"task": "WEEKLY_VALIDATION", "schedule": "0 0 * * 0", "enabled": True},
            {"task": "WEEKLY_MODEL_RETRAINING", "schedule": "0 2 * * 0", "enabled": False},  # Default disabled
            {"task": "MONTHLY_RESEARCH_REPORT", "schedule": "0 0 1 * *", "enabled": True},
        ]

    def list_schedules(self) -> List[Dict[str, Any]]:
        return self._schedules

    def toggle_schedule(self, task_name: str, enabled: bool) -> bool:
        for s in self._schedules:
            if s["task"] == task_name:
                s["enabled"] = enabled
                return True
        return False
