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

    def save_artifact(self, run_id: str, stage_name: str, filename: str, content: Any) -> str:
        stage_dir = self.artifacts_dir / run_id / stage_name
        stage_dir.mkdir(parents=True, exist_ok=True)
        filepath = stage_dir / filename
        if isinstance(content, (dict, list)):
            with open(filepath, "w") as f:
                json.dump(content, f, indent=2)
        elif isinstance(content, str):
            with open(filepath, "w") as f:
                f.write(content)
        else:
            with open(filepath, "wb") as f:
                f.write(content)
        return str(filepath)

    def register_artifact(self, run_id: str, stage_name: str, filename: str, content: Any) -> Dict[str, Any]:
        filepath = self.save_artifact(run_id, stage_name, filename, content)
        chk = self.calculate_checksum(filepath)
        size = os.path.getsize(filepath)
        return {
            "run_id": run_id,
            "stage_name": stage_name,
            "filename": filename,
            "filepath": filepath,
            "checksum": chk,
            "size_bytes": size,
        }

    def exists(self, run_id: str, stage_name: str, filename: str) -> bool:
        filepath = self.artifacts_dir / run_id / stage_name / filename
        return filepath.exists()

    def calculate_checksum(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            return "00000000"
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]
