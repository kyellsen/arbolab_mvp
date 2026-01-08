from pathlib import Path

import yaml
from arbolab_logger import get_logger
from pydantic import BaseModel, ConfigDict, Field

logger = get_logger(__name__)

DEFAULT_CONFIG_FILENAME = "config.yaml"

class LabConfig(BaseModel):
    """
    Immutable configuration for the ArboLab runtime.
    """
    model_config = ConfigDict(frozen=True)

    config_version: str = Field(default="1.0.0", description="Schema version")
    
    # Persisted Roots
    input_path: str | None = Field(default=None, description="Path to input data root (relative or absolute)")
    results_path: str | None = Field(default=None, description="Path to results root (relative or absolute)")
    
    enabled_plugins: list[str] = Field(default_factory=list, description="Allow-list of enabled plugin entry points")
    
    # Plugin specific settings (namespaced)
    plugins: dict = Field(default_factory=dict, description="Plugin-specific configuration")

def load_config(workspace_root: Path) -> LabConfig:
    """
    Load configuration from workspace_root with fallback to defaults.
    """
    config_path = workspace_root / DEFAULT_CONFIG_FILENAME
    
    if not config_path.exists():
        logger.debug(f"No config found at {config_path}, using defaults.")
        return LabConfig()
        
    try:
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        logger.debug(f"Loaded config from {config_path}")
        return LabConfig(**data)
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration from {config_path}: {e}") from e

def create_default_config(workspace_root: Path, 
                          initial_input: Path | None = None, 
                          initial_results: Path | None = None) -> Path:
    """
    Bootstrap a new configuration file if it doesn't exist.
    """
    config_path = workspace_root / DEFAULT_CONFIG_FILENAME
    if config_path.exists():
        return config_path
        
    # Convert paths to strings for storage
    input_str = str(initial_input) if initial_input else None
    results_str = str(initial_results) if initial_results else None
        
    config = LabConfig(
        input_path=input_str,
        results_path=results_str
    ) 
    
    # Convert to dict, exclude defaults if needed, but for bootstrap we dump everything
    data = config.model_dump(mode='json')
    
    logger.info(f"Bootstrapping default configuration at {config_path}")
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False)
        
    return config_path
