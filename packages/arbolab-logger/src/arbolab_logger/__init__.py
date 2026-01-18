"""Rich-based logging helpers for the Arbolab Lab runtime."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from rich.console import Console
from rich.logging import RichHandler

__all__ = [
    "LoggerConfig",
    "configure_logger",
    "get_logger",
    "get_logger_config",
]


def _coerce_level(level: int | str) -> int:
    """Return a numeric log level for ``level``.

    Args:
        level: Logging level specified as integer or textual label.

    Returns:
        The numeric logging level that the stdlib expects.
    """

    if isinstance(level, int):
        return level
    resolved = level.upper()
    numeric = getattr(logging, resolved, None)
    if isinstance(numeric, int):
        return numeric
    msg = f"Unknown logging level: {level!r}"
    raise ValueError(msg)


class LoggerConfig(BaseModel):
    """Immutable configuration describing how loggers should behave."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    name: str = Field(
        default="arbolab",
        description="Base name for loggers emitted by the workspace.",
    )
    level: int | str = Field(
        default="INFO",
        description="Logging level as numeric value or standard text label.",
    )
    propagate: bool = Field(
        default=True, description="Whether records propagate to ancestor loggers."
    )
    colorize: bool = Field(
        default=True,
        description="Whether Rich should emit coloured output.",
    )
# ... (skipping unchanged fields)

    markup: bool = Field(
        default=True,
        description="Whether log messages contain Rich markup that must be parsed.",
    )
    show_time: bool = Field(
        default=True,
        description="Whether the handler prints timestamps in its dedicated column."
    )
    show_level: bool = Field(
        default=True,
        description="Controls whether the handler prints the textual log level.",
    )
    show_path: bool = Field(
        default=True,
        description="Controls whether the handler prints source file information.",
    )
    log_time_format: str | None = Field(
        default="[%Y-%m-%d %H:%M:%S]",
        description="`time.strftime` pattern applied to log timestamps.",
    )
    omit_repeated_times: bool = Field(
        default=False,
        description="Hide repeated timestamps to reduce noise in dense logs.",
    )
    enable_link_path: bool = Field(
        default=True,
        description="Whether Rich should render source paths as clickable links.",
    )
    rich_tracebacks: bool = Field(
        default=True,
        description="Enable Rich tracebacks for exceptions handled by logging.",
    )
    tracebacks_width: int | None = Field(
        default=None,
        description="Optional soft wrap width for Rich tracebacks.",
    )
    console_width: int | None = Field(
        default=None,
        description="Optional width override for the Rich console.",
    )
    force_terminal: bool = Field(
        default=True,
        description=(
            "Force Rich to treat the output stream like a terminal so colours "
            "always show up in VS Code, PyCharm, and Jupyter Lab."
        ),
    )
    log_to_stderr: bool = Field(
        default=True,
        description="Send log output to stderr instead of stdout when True.",
    )
    enable_profiling: bool = Field(
        default=False,
        description=(
            "Reserved flag: when True, profiling helpers are allowed to emit logs."
        ),
    )
    log_to_file: bool = Field(
        default=False,
        description="When True, also write logs to a file defined by ``log_file_path``.",
    )
    log_file_path: str | None = Field(
        default=None,
        description=(
            "Absolute path to the log file when ``log_to_file`` is enabled. "
            "If omitted, file logging is deferred until a path is provided."
        ),
    )
    file_level: int | str | None = Field(
        default=None,
        description="Optional log level override for the file handler; defaults to ``level``.",
    )
    file_message_format: str = Field(
        default="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        description="Formatter used for the file handler.",
    )
    message_format: str = Field(
        default="%(message)s",
        description="Formatter string for the handler attached to Rich.",
    )

    @field_validator("level")
    @classmethod
    def _validate_level(cls, value: int | str) -> int | str:
        """Validate that ``value`` is either numeric or resolves to a log level."""

        if isinstance(value, str):
            return value.upper()
        if value < 0:
            msg = "Logging level must be non-negative"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def _validate_file_logging(self) -> LoggerConfig:
        """Ensure file logging paths are valid when provided."""

        if self.log_to_file and self.log_file_path is not None and not self.log_file_path:
            msg = "log_file_path must be set when log_to_file is enabled."
            raise ValueError(msg)
        return self

    def with_updates(self, **updates: Any) -> LoggerConfig:
        """Return a copy of the configuration with ``updates`` applied.

        Args:
            **updates: Keyword arguments that override fields on the model.

        Returns:
            A new :class:`LoggerConfig` instance with the merged data.
        """

        data = self.model_dump()
        data.update(updates)
        return LoggerConfig(**data)


def _build_console(config: LoggerConfig) -> Console:
    """Return a Rich console configured according to ``config``.

    Args:
        config: Logger configuration describing console behaviour.

    Returns:
        A `rich.console.Console` object with the requested options applied.
    """

    return Console(
        stderr=config.log_to_stderr,
        force_terminal=config.force_terminal,
        width=config.console_width,
        no_color=not config.colorize,
    )


def _build_handler(config: LoggerConfig) -> RichHandler:
    """Return a Rich handler configured according to ``config``.

    Args:
        config: Logger configuration describing handler behaviour.

    Returns:
        A configured `RichHandler` ready to be attached to a logger.
    """

    handler_kwargs: dict[str, Any] = {
        "console": _build_console(config),
        "show_time": config.show_time,
        "show_level": config.show_level,
        "show_path": config.show_path,
        "rich_tracebacks": config.rich_tracebacks,
        "tracebacks_width": config.tracebacks_width,
        "markup": config.markup,
        "enable_link_path": config.enable_link_path,
        "omit_repeated_times": config.omit_repeated_times,
    }
    if config.log_time_format is not None:
        handler_kwargs["log_time_format"] = config.log_time_format

    handler = RichHandler(**handler_kwargs)
    handler.setFormatter(logging.Formatter(config.message_format))
    handler._arbolab_signature = _rich_handler_signature(config)  # type: ignore[attr-defined]
    return handler


def _remove_file_handlers(logger: logging.Logger) -> None:
    """Remove file handlers from ``logger``."""

    for existing in list(logger.handlers):
        if isinstance(existing, logging.FileHandler):
            logger.removeHandler(existing)
            existing.close()


def _sync_rich_handlers(
    logger: logging.Logger,
    *,
    config: LoggerConfig,
    level: int,
    signature: tuple[object, ...],
) -> None:
    """Ensure Rich handlers are present and match ``config``."""

    for existing in list(logger.handlers):
        if isinstance(existing, RichHandler):
            current = getattr(existing, "_arbolab_signature", None)
            if current != signature:
                logger.removeHandler(existing)
                existing.close()
    if not any(isinstance(handler, RichHandler) for handler in logger.handlers):
        handler = _build_handler(config)
        handler.setLevel(level)
        logger.addHandler(handler)


def _sync_file_handlers(logger: logging.Logger, *, config: LoggerConfig) -> None:
    """Ensure file handlers match ``config`` or are removed."""

    if config.log_to_file and config.log_file_path:
        desired_path = Path(config.log_file_path).expanduser().resolve(strict=False)
        matching_handler: logging.FileHandler | None = None
        for existing in list(logger.handlers):
            if isinstance(existing, logging.FileHandler):
                existing_path = Path(existing.baseFilename).resolve(strict=False)
                if existing_path == desired_path:
                    matching_handler = existing
                else:
                    logger.removeHandler(existing)
                    existing.close()
        if matching_handler is None:
            file_handler = _build_file_handler(config)
            logger.addHandler(file_handler)
        return

    _remove_file_handlers(logger)


def _apply_handler_levels(
    logger: logging.Logger,
    *,
    config: LoggerConfig,
    level: int,
    signature: tuple[object, ...],
) -> None:
    """Apply log levels and formatters to handlers owned by ``logger``."""

    for existing in logger.handlers:
        target_level = level
        if isinstance(existing, logging.FileHandler):
            target_level = _coerce_level(config.file_level or config.level)
            existing.setFormatter(logging.Formatter(config.file_message_format))
        elif isinstance(existing, RichHandler):
            existing.setFormatter(logging.Formatter(config.message_format))
            existing._arbolab_signature = signature  # type: ignore[attr-defined]
        existing.setLevel(target_level)


def _ensure_handler(logger: logging.Logger, config: LoggerConfig) -> None:
    """Attach a Rich handler to ``logger`` when missing and set up its options.

    Args:
        logger: Logger that should be configured.
        config: Active logging configuration.
    """

    level = _coerce_level(config.level)
    logger.setLevel(level)

    signature = _rich_handler_signature(config)
    _sync_rich_handlers(logger, config=config, level=level, signature=signature)
    _sync_file_handlers(logger, config=config)
    _apply_handler_levels(logger, config=config, level=level, signature=signature)

    logger.propagate = config.propagate


def _build_file_handler(config: LoggerConfig) -> logging.FileHandler:
    """Return a file handler when file logging is enabled."""

    if not config.log_file_path:
        msg = "log_file_path must be set when building a file handler."
        raise ValueError(msg)
    path = Path(config.log_file_path).expanduser().resolve(strict=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(path)
    level = _coerce_level(config.file_level or config.level)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(config.file_message_format))
    return handler


def _rich_handler_signature(config: LoggerConfig) -> tuple[object, ...]:
    """Return a stable signature for Rich handler configuration."""

    return (
        config.colorize,
        config.show_time,
        config.show_level,
        config.show_path,
        config.log_time_format,
        config.omit_repeated_times,
        config.enable_link_path,
        config.rich_tracebacks,
        config.tracebacks_width,
        config.markup,
        config.console_width,
        config.force_terminal,
        config.log_to_stderr,
    )


def _clear_handlers(logger: logging.Logger) -> None:
    """Remove and close all handlers from ``logger``."""

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


_LOGGER_STATE: dict[str, LoggerConfig] = {"config": LoggerConfig()}


def configure_logger(config: LoggerConfig) -> logging.Logger:
    """Configure and return a logger according to ``config``.

    Args:
        config: Desired logger configuration.

    Returns:
        The configured :class:`logging.Logger` instance.
    """

    _LOGGER_STATE["config"] = config
    logger = logging.getLogger(config.name)
    _clear_handlers(logger)
    _ensure_handler(logger, config)
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a logger. 
    
    If name is None or matches the configured root name, it returns the configured root logger (with handlers).
    If name is a child, it returns a standard logger that propagates to the root.
    """

    current = _LOGGER_STATE["config"]
    
    # If no name -> use root name.
    target_name = name if name else current.name

    # If target matches the base configuration name (e.g. "arbolab"),
    # we ensure handlers are attached (RichHandler).
    if target_name == current.name:
        logger = logging.getLogger(current.name)
        _ensure_handler(logger, current)
        return logger

    # Otherwise (e.g. "arbolab.database"), standard propagation behavior.
    # We do NOT manually attach handlers. It propagates to "arbolab".
    return logging.getLogger(target_name)


def get_logger_config() -> LoggerConfig:
    """Return the active :class:`LoggerConfig` instance.

    Returns:
        The immutable configuration currently used by the logger helpers.
    """

    return _LOGGER_STATE["config"]
