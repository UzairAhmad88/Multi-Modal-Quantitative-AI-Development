"""
Hardware Detector and Device Selector.
Detects CUDA GPU availability with safe CPU fallback.
"""

from typing import Dict, Any
import torch
import psutil


class HardwareDetector:
    """Detects available hardware compute resources."""

    @staticmethod
    def get_device_info() -> Dict[str, Any]:
        cuda_available = torch.cuda.is_available()
        device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"
        cpu_count = psutil.cpu_count(logical=True)
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)

        return {
            "device": "cuda" if cuda_available else "cpu",
            "cuda_available": cuda_available,
            "device_name": device_name,
            "cpu_cores": cpu_count,
            "total_ram_gb": ram_gb
        }
