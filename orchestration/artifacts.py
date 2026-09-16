"""
Artifact Manager for Orchestration OS.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ArtifactManager:
    """Manages storing, loading, and checksumming orchestration artifacts."""

    def __init__(self, artifacts_dir: Optional[str] = None):
        if artifacts_dir is None:
            artifacts_dir = os.path.join(os.getcwd(), "artifacts", "orchestration")
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def calculate_checksum(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            return "00000000"
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]
