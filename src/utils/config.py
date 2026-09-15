from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv

from src.utils.paths import ROOT

# Load environment variables from .env if present
load_dotenv(ROOT / ".env")


class Config:
    """Centralized configuration manager loading YAML configs and environment overrides."""

    def __init__(self, config_dir: Path | str | None = None):
        self.config_dir = Path(config_dir) if config_dir else ROOT / "configs"
        self._raw_config: Dict[str, Any] = {}
        self.reload()

    def reload(self) -> None:
        """Reload all configuration files from the config directory."""
        config_files = ["config.yaml", "data.yaml", "models.yaml", "portfolio.yaml", "risk.yaml"]
        merged: Dict[str, Any] = {}

        for filename in config_files:
            file_path = self.config_dir / filename
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = yaml.safe_load(f) or {}
                    merged.update(content)

        # Environment variable overrides
        merged["env"] = os.getenv("APP_ENV", "development")
        merged["data_mode"] = os.getenv("DATA_MODE", "demo")

        self._raw_config = merged
        self.validate()

    def validate(self) -> bool:
        """Validate core configuration parameters."""
        project = self._raw_config.get("project", {})
        if not project.get("name"):
            self._raw_config.setdefault("project", {})["name"] = "multi_modal_quant_ai"

        data_cfg = self._raw_config.get("data", {})
        if not data_cfg.get("universe"):
            self._raw_config.setdefault("data", {})["universe"] = [
                "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "JPM", "XOM"
            ]

        portfolio_cfg = self._raw_config.get("portfolio", {})
        if "max_position" not in portfolio_cfg:
            self._raw_config.setdefault("portfolio", {})["max_position"] = 0.25

        risk_cfg = self._raw_config.get("risk", {})
        if "max_drawdown" not in risk_cfg:
            self._raw_config.setdefault("risk", {})["max_drawdown"] = 0.20

        return True

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a top-level configuration key or nested dot-separated key."""
        parts = key.split(".")
        val = self._raw_config
        for part in parts:
            if isinstance(val, dict) and part in val:
                val = val[part]
            else:
                return default
        return val

    def to_dict(self) -> Dict[str, Any]:
        """Return the complete merged configuration as a dictionary."""
        return self._raw_config.copy()


# Global singleton instance
_default_config: Config | None = None


def get_config(config_dir: Path | str | None = None) -> Config:
    """Get or create the global Config instance."""
    global _default_config
    if _default_config is None or config_dir is not None:
        _default_config = Config(config_dir)
    return _default_config
