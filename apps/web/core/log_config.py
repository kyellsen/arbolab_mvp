"""Feature flags and configuration for the log drawer."""

from pydantic_settings import BaseSettings


class LogFeatureFlags(BaseSettings):
    """Feature flags for log drawer tabs.
    
    Set environment variables with ARBOLAB_ prefix to override defaults.
    Example: ARBOLAB_LOG_SYSTEM_ENABLED=false
    """
    
    # Enable/disable individual log tabs
    LOG_RECIPE_ENABLED: bool = True     # Recipe execution steps
    LOG_SYSTEM_ENABLED: bool = True     # arbolab-logger file logs
    
    # Polling configuration
    LOG_POLL_INTERVAL_MS: int = 3000    # Interval in milliseconds (readable + lower traffic)
    
    # Response limits
    LOG_MAX_ENTRIES: int = 200          # Max entries per request
    
    class Config:
        env_prefix = "ARBOLAB_"
        case_sensitive = True


# Singleton instance - import this in routes/templates
log_flags = LogFeatureFlags()
