"""
Resource Manager for Execution Monitoring.
Tracks CPU, RAM, Disk, and runtime limits, enforcing local resource boundaries.
"""

from typing import Dict, Any
import os
import sys
import psutil
import time


class ResourceManager:
    """Monitors system resource usage and checks resource constraints."""

    def __init__(self, max_memory_gb: float = 8.0, max_runtime_minutes: float = 120.0):
        self.max_memory_gb = max_memory_gb
        self.max_runtime_seconds = max_runtime_minutes * 60.0
        self.start_time = time.time()

    def get_resource_usage(self) -> Dict[str, Any]:
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        mem_gb = mem_info.rss / (1024 ** 3)
        cpu_pct = psutil.cpu_percent(interval=None)
        elapsed_sec = time.time() - self.start_time

        return {
            "memory_usage_gb": round(mem_gb, 3),
            "max_memory_limit_gb": self.max_memory_gb,
            "cpu_percent": round(cpu_pct, 1),
            "elapsed_seconds": round(elapsed_sec, 1),
            "max_runtime_seconds": self.max_runtime_seconds,
        }

    def check_limits(self):
        usage = self.get_resource_usage()
        if usage["memory_usage_gb"] > self.max_memory_gb:
            raise MemoryError(f"Memory limit exceeded: {usage['memory_usage_gb']:.2f} GB > {self.max_memory_gb} GB limit.")

        if usage["elapsed_seconds"] > self.max_runtime_seconds:
            raise TimeoutError(f"Runtime limit exceeded: {usage['elapsed_seconds']:.1f}s > {self.max_runtime_seconds}s limit.")
