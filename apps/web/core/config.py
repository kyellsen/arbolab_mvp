from pathlib import Path
from pydantic import Field
from pydantic_settings import SettingsConfigDict
from arbolab.config import LabConfig

class WebConfig(LabConfig):
    """
    SaaS-specific configuration for Arbolab.
    Extends the base LabConfig with PostgreSQL and Auth settings.
    """
    model_config = SettingsConfigDict(
        env_prefix="ARBO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database (SaaS)
    # Default to arbolab for local dev with docker compose
    database_url: str | None = Field(
        default="postgresql://arbolab:arbolab@db:5432/arbolab",
        description="Connection string for the SaaS database"
    )

    # Security
    secret_key: str = Field(
        default="change_me_in_production",
        description="Secret key for session signing"
    )

def load_web_config() -> WebConfig:
    """Load the SaaS configuration."""
    return WebConfig()
