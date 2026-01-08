import os
from pathlib import Path
from typing import Any

import yaml
from arbolab_logger import get_logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = get_logger(__name__)

DEFAULT_CONFIG_FILENAME = "config.yaml"

class LabConfig(BaseSettings):
    """
    Configuration for the ArboLab runtime.
    Reads from Environment Variables (ARBO_...) and optional config.yaml.
    """
    model_config = SettingsConfigDict(
        env_prefix="ARBO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    config_version: str = Field(default="1.0.0", description="Schema version")

    # Persisted Roots (12-Factor)
    # Default data root is ./data relative to CWD, but can be overridden by ARBO_DATA_ROOT
    data_root: Path = Field(default=Path("./data"), description="Root directory for all data")
    
    # Database (SaaS)
    # Default to arbolab for local dev with docker compose
    database_url: str | None = Field(
        default="postgresql://arbolab:arbolab@db:5432/arbolab",
        description="Connection string for the SaaS database"
    )

    # Explicit Overrides (Legacy/Flexible)
    input_path: str | None = Field(default=None, description="Explicit path to input root")
    results_path: str | None = Field(default=None, description="Explicit path to results root")

    # Derived paths (can be overridden, but usually derived from data_root)
    input_dir_name: str = "input"
    workspace_dir_name: str = "workspace"

    enabled_plugins: list[str] = Field(default_factory=list, description="Allow-list of enabled plugin entry points")
    
    # Plugin specific settings (namespaced)
    plugins: dict[str, Any] = Field(default_factory=dict, description="Plugin-specific configuration")

    @property
    def input_root(self) -> Path:
        return self.data_root / self.input_dir_name

    @property
    def workspace_root(self) -> Path:
        return self.data_root / self.workspace_dir_name

    def ensure_directories(self):
        """Ensure all data directories exist."""
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.input_root.mkdir(parents=True, exist_ok=True)
        self.workspace_root.mkdir(parents=True, exist_ok=True)


def load_config(workspace_root: Path | None = None) -> LabConfig:
    """
    Load configuration. 
    Priority: Env Vars > config.yaml > Defaults.
    
    If workspace_root is provided, we try to look for config.yaml there.
    Otherwise we rely on defaults/env vars.

    Raises:
        RuntimeError: If the config file exists but cannot be parsed.
    """
    # 1. Start with defaults + env vars
    config = LabConfig()
    
    # 2. If a config file exists, we might want to overlay it?
    # For now, strictly following 12-factor for the major paths.
    # But if we need to load legacy yaml:
    
    target_root = workspace_root or config.data_root
    config_path = target_root / DEFAULT_CONFIG_FILENAME

    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                file_data = yaml.safe_load(f) or {}
        except Exception as exc:
            raise RuntimeError(f"Failed to read {config_path}: {exc}") from exc

        if not isinstance(file_data, dict):
            raise RuntimeError(f"Config file {config_path} must contain a mapping.")

        env_prefix = str(LabConfig.model_config.get("env_prefix", ""))
        updates: dict[str, Any] = {}
        for key, value in file_data.items():
            if key not in LabConfig.model_fields:
                continue
            env_key = f"{env_prefix}{key}".upper()
            if env_key in os.environ:
                continue
            updates[key] = value

        if updates:
            config = config.model_copy(update=updates)

    logger.debug(f"Loaded config: DATA_ROOT={config.data_root}, DB_URL={'Set' if config.database_url else 'Unset'}")
    return config


def create_default_config(
    workspace_root: Path,
    initial_input: Path | None = None,
    initial_results: Path | None = None,
) -> Path:
    """
    Creates a basic config.yaml if it doesn't exist.

    Returns:
        The path to the config file.
    """
    config_path = workspace_root / DEFAULT_CONFIG_FILENAME
    if config_path.exists():
        return config_path

    config_data = {
        "config_version": "1.0.0",
        "input_path": str(initial_input) if initial_input else None,
        "results_path": str(initial_results) if initial_results else None
    }
    
    # Filter None
    config_data = {k: v for k, v in config_data.items() if v is not None}

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, sort_keys=False)
        logger.info(f"Created default config at {config_path}")
    except Exception as e:
        logger.warning(f"Failed to create default config: {e}")
    return config_path
