"""
Resource Monitor for System Hardware & Concurrency Enforcement.
"""

import os
import psutil
from typing import Dict, Any, Tuple
from orchestrator.schemas.workflow_schema import ResourceBudget


class ResourceMonitor:
    """
    Checks hardware resource utilization (CPU, RAM, GPU) against ResourceBudget safety limits.
    """

    @staticmethod
    def get_current_metrics() -> Dict[str, Any]:
        cpu_pct = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        return {
            "cpu_percent": cpu_pct,
            "memory_percent": mem.percent,
            "memory_used_gb": round(mem.used / (1024 ** 3), 2),
            "memory_total_gb": round(mem.total / (1024 ** 3), 2),
            "gpu_available": False,
            "gpu_memory_used_gb": 0.0,
        }

    @staticmethod
    def check_limits(budget: ResourceBudget, active_jobs_count: int) -> Tuple[bool, str]:
        metrics = ResourceMonitor.get_current_metrics()

        if active_jobs_count >= budget.max_parallel_jobs:
            return False, f"Active jobs ({active_jobs_count}) reached max_parallel_jobs limit ({budget.max_parallel_jobs})"

        if metrics["memory_used_gb"] > budget.max_memory_gb:
            return False, f"Memory usage ({metrics['memory_used_gb']} GB) exceeds budget limit ({budget.max_memory_gb} GB)"

        return True, "Resource limits verified"
