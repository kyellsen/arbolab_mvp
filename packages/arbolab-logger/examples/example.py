"""Linear example showing how to configure and use the arbolab-logger helpers."""

from __future__ import annotations

from arbolab_logger import (  # type: ignore[import-untyped]
    LoggerConfig,
    configure_logger,
    get_logger,
    get_logger_config,
)

# Configure the Rich handler with debug-level filtering and custom formatting.
# show_time defaults to False so only the handlers built-in timestamp column stays hidden.
configure_logger(
    LoggerConfig(
        name="arbolab.examples.logger",
        level="DEBUG",
        show_path=True,
        show_level=True,
        message_format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )
)

# Emit logs across levels so the formatter is populated with different records.
logger = get_logger()
logger.debug("debug → tracing the computation details")
logger.info("info → high-level progress updates")
logger.warning("warning → recoverable issue detected")
logger.error("error → operation failed with recoverable exception")
logger.critical("critical → unrecoverable, escalation needed")

print("\nCurrent configuration:", get_logger_config())
print("Raising the logger threshold to WARNING to suppress debug/info.")

# Apply a new configuration with a higher log level while keeping other settings.
configure_logger(get_logger_config().with_updates(level="WARNING"))
logger = get_logger()
logger.debug("debug → this should no longer appear")
logger.info("info → neither should this line")
logger.warning("warning → still visible after raising the level")
logger.error("error → still emitted")
logger.critical("critical → unrecoverable, escalation needed")
