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
    # Default to sqlite for local dev if not set, but production should set ARBO_DATABASE_URL
    database_url: str | None = Field(default=None, description="Connection string for the SaaS database")

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
                # Update config with file data, but Env vars should effectively override 
                # (pydantic BaseSettings usually prioritizes Env over init args if configured, 
                # but here we are manual. Let's start simple: Env > Defaults. Config file is secondary/deprecated for paths?)
                
                # Actually, standard behavior: Env > Secrets > Config File > Defaults.
                # If we want to support config.yaml, we should integrate it into settings sources.
                # For this MVP step, let's just log it.
                logger.debug(f"Found config at {config_path}, but using Env/Defaults for critical paths.")
        except Exception as e:
            logger.warning(f"Failed to read {config_path}: {e}")

    logger.debug(f"Loaded config: DATA_ROOT={config.data_root}, DB_URL={'Set' if config.database_url else 'Unset'}")
    return config
