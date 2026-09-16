"""
Artifact Store: Registers and indexes experiment outputs, data files, models, plots, and reports with content hashing.
"""

from typing import Dict, Any, List, Optional
import hashlib
from pathlib import Path


class ArtifactStore:
    """Stores artifact paths and metadata for experiment traceability."""

    def __init__(self):
        self.artifacts_index: Dict[str, Dict[str, Any]] = {}

    def register_artifact(
        self,
        experiment_id: str,
        artifact_type: str,
        file_path: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """Indexes an artifact file path with SHA256 checksum where available."""
        p = Path(file_path)
        content_hash = ""
        if p.exists() and p.is_file():
            try:
                content_hash = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
            except Exception:
                content_hash = "UNHASHABLE"

        entry = {
            "experiment_id": experiment_id,
            "artifact_type": artifact_type,
            "file_path": str(file_path),
            "content_hash": content_hash,
            "description": description
        }

        art_id = f"ART-{experiment_id}-{artifact_type.upper()}"
        self.artifacts_index[art_id] = entry
        return entry
