"""Tests for the arbolab-logger helpers."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from arbolab_logger import (
    LoggerConfig,
    _build_file_handler,
    _coerce_level,
    _ensure_handler,
    _rich_handler_signature,
    configure_logger,
    get_logger,
    get_logger_config,
)
from rich.logging import RichHandler


def _get_rich_handler(logger: logging.Logger) -> RichHandler:
    """Return the first Rich handler registered on ``logger``."""

    for handler in logger.handlers:
        if isinstance(handler, RichHandler):
            return handler
    raise AssertionError("Logger is missing a RichHandler instance")


def test_configure_logger_installs_rich_handler() -> None:
    """configure_logger should attach a Rich handler at the configured level."""

    config = LoggerConfig(name="arbolab.tests")
    logger = configure_logger(config)

    assert logger.level == logging.INFO
    handler = _get_rich_handler(logger)
    assert handler.level == logging.INFO
    assert handler.console is not None


def test_get_logger_with_custom_name_preserves_base_config() -> None:
    """get_logger should clone the active config when overriding the name."""

    base = LoggerConfig(name="arbolab.base", level="WARNING")
    configure_logger(base)
    derived = get_logger(name="arbolab.feature")

    assert derived.name == "arbolab.feature"
    assert get_logger_config().name == "arbolab.base"


def test_with_updates_creates_new_config() -> None:
    """LoggerConfig.with_updates returns a detached copy."""

    config = LoggerConfig(name="arbolab.copy")
    updated = config.with_updates(level="DEBUG")

    assert updated is not config
    assert updated.level == "DEBUG"
    assert config.level == "INFO"


def test_disabling_color_turns_off_rich_colors() -> None:
    """Color output can be disabled via the config."""

    config = LoggerConfig(name="arbolab.nocolor", colorize=False)
    logger = configure_logger(config)
    handler = _get_rich_handler(logger)

    assert handler.console.no_color is True


def test_coerce_level_accepts_strings_and_numbers() -> None:
    """_coerce_level resolves textual and numeric levels."""

    assert _coerce_level("debug") == logging.DEBUG
    assert _coerce_level(logging.WARNING) == logging.WARNING


def test_coerce_level_rejects_unknown_value() -> None:
    """Unknown log levels raise a clear ValueError."""

    with pytest.raises(ValueError, match="Unknown logging level"):
        _coerce_level("not-a-level")


def test_logger_config_forces_uppercase_levels() -> None:
    """LoggerConfig enforces uppercase string labels."""

    config = LoggerConfig(level="debug")
    assert config.level == "DEBUG"


def test_logger_config_accepts_numeric_level() -> None:
    """Numeric logging levels are preserved."""

    config = LoggerConfig(level=logging.ERROR)
    assert config.level == logging.ERROR


def test_logger_config_rejects_negative_level() -> None:
    """Negative logging levels are invalid."""

    with pytest.raises(ValueError, match="Logging level must be non-negative"):
        LoggerConfig(level=-5)


def test_configure_logger_sets_propagation_flag() -> None:
    """Propagation switches stored in the configuration reach the logger."""

    config = LoggerConfig(name="arbolab.propagate", propagate=True)
    logger = configure_logger(config)

    assert logger.propagate is True


def test_get_logger_reuses_existing_handler() -> None:
    """Repeated get_logger calls do not add duplicate handlers."""

    base = LoggerConfig(name="arbolab.reuse")
    logger = configure_logger(base)
    handler_count = len(logger.handlers)

    derived = get_logger()

    assert derived is logger
    assert len(logger.handlers) == handler_count


def test_logger_config_allows_deferred_file_logging() -> None:
    """log_to_file can be enabled before a file path is available."""

    config = LoggerConfig(name="arbolab.deferred", log_to_file=True)
    logger = configure_logger(config)

    assert not any(isinstance(h, logging.FileHandler) for h in logger.handlers)


def test_logger_config_rejects_empty_file_path() -> None:
    """log_to_file requires a non-empty log_file_path when provided."""

    with pytest.raises(ValueError, match="log_file_path must be set when log_to_file is enabled"):
        LoggerConfig(name="arbolab.empty-path", log_to_file=True, log_file_path="")


def test_build_file_handler_requires_path() -> None:
    """_build_file_handler refuses configs without a file path."""

    config = LoggerConfig(name="arbolab.no-path", log_to_file=True)
    with pytest.raises(
        ValueError, match="log_file_path must be set when building a file handler"
    ):
        _build_file_handler(config)


def test_configure_logger_closes_existing_handlers(tmp_path: Path) -> None:
    """Reconfiguring the logger closes existing handlers."""

    log_path = tmp_path / "app.log"
    config = LoggerConfig(
        name="arbolab.close",
        log_to_file=True,
        log_file_path=str(log_path),
    )
    logger = configure_logger(config)
    file_handler = next(
        handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)
    )
    assert file_handler.stream is not None
    assert file_handler.stream.closed is False

    configure_logger(LoggerConfig(name="arbolab.close"))

    assert file_handler not in logging.getLogger("arbolab.close").handlers
    assert file_handler.stream is None or file_handler.stream.closed is True


def test_ensure_handler_removes_file_handler_when_disabled(tmp_path: Path) -> None:
    """File handlers are removed when file logging is disabled."""

    logger = logging.getLogger("arbolab.file-toggle")
    logger.handlers.clear()
    config = LoggerConfig(
        name="arbolab.file-toggle",
        log_to_file=True,
        log_file_path=str(tmp_path / "one.log"),
    )
    _ensure_handler(logger, config)
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

    disabled = LoggerConfig(name="arbolab.file-toggle", log_to_file=False)
    _ensure_handler(logger, disabled)

    assert not any(isinstance(h, logging.FileHandler) for h in logger.handlers)


def test_ensure_handler_replaces_file_handler_when_path_changes(tmp_path: Path) -> None:
    """Changing the file path replaces the previous file handler."""

    logger = logging.getLogger("arbolab.file-replace")
    logger.handlers.clear()
    first_path = (tmp_path / "one.log").resolve()
    config = LoggerConfig(
        name="arbolab.file-replace",
        log_to_file=True,
        log_file_path=str(first_path),
    )
    _ensure_handler(logger, config)
    first_handler = next(
        handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)
    )

    second_path = (tmp_path / "two.log").resolve()
    updated = LoggerConfig(
        name="arbolab.file-replace",
        log_to_file=True,
        log_file_path=str(second_path),
    )
    _ensure_handler(logger, updated)

    handlers = [
        handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)
    ]
    assert len(handlers) == 1
    assert Path(handlers[0].baseFilename) == second_path
    assert first_handler.stream is None or first_handler.stream.closed is True


def test_ensure_handler_reuses_file_handler_when_path_unchanged(tmp_path: Path) -> None:
    """File handlers are kept when the file path stays the same."""

    logger = logging.getLogger("arbolab.file-keep")
    logger.handlers.clear()
    log_path = (tmp_path / "keep.log").resolve()
    config = LoggerConfig(
        name="arbolab.file-keep",
        log_to_file=True,
        log_file_path=str(log_path),
    )
    _ensure_handler(logger, config)
    _ensure_handler(logger, config)

    handlers = [
        handler for handler in logger.handlers if isinstance(handler, logging.FileHandler)
    ]
    assert len(handlers) == 1
    assert Path(handlers[0].baseFilename) == log_path


def test_configure_logger_creates_missing_log_directory(tmp_path: Path) -> None:
    """configure_logger creates parent directories for file logging."""

    log_path = tmp_path / "nested" / "logs" / "app.log"
    config = LoggerConfig(
        name="arbolab.makedirs",
        log_to_file=True,
        log_file_path=str(log_path),
    )
    logger = configure_logger(config)
    logger.warning("created")
    for handler in logger.handlers:
        handler.flush()

    assert log_path.exists()


def test_rich_handler_is_rebuilt_when_config_changes() -> None:
    """Rich handlers are replaced when the configuration signature changes."""

    logger = logging.getLogger("arbolab.rich")
    logger.handlers.clear()
    config = LoggerConfig(name="arbolab.rich", show_time=True)
    _ensure_handler(logger, config)
    first_handler = _get_rich_handler(logger)
    first_signature = getattr(first_handler, "_arbolab_signature", None)
    assert first_signature == _rich_handler_signature(config)

    updated = LoggerConfig(name="arbolab.rich", show_time=False)
    _ensure_handler(logger, updated)
    second_handler = _get_rich_handler(logger)
    second_signature = getattr(second_handler, "_arbolab_signature", None)

    assert second_handler is not first_handler
    assert second_signature == _rich_handler_signature(updated)
