"""Integration coverage for arbolab_logger."""

from __future__ import annotations

import logging
from pathlib import Path

from arbolab_logger import LoggerConfig, configure_logger, get_logger, get_logger_config
from rich.logging import RichHandler


def _flush_handlers(logger: logging.Logger) -> None:
    """Flush all handlers attached to ``logger``."""

    for handler in logger.handlers:
        handler.flush()


def test_logger_integration_full_flow(tmp_path: Path) -> None:
    """Exercise the logger as it would be used in a small project."""

    log_dir = tmp_path / "logs"
    first_log = log_dir / "app.log"
    second_log = log_dir / "app-2.log"

    config = LoggerConfig(
        name="arbolab.integration",
        level="INFO",
        log_to_file=True,
        log_file_path=str(first_log),
        file_level="WARNING",
        message_format="%(levelname)s:%(message)s",
        file_message_format="%(levelname)s:%(message)s",
        show_time=False,
        show_level=True,
        show_path=False,
        markup=False,
        colorize=False,
    )
    logger = configure_logger(config)
    assert any(isinstance(h, RichHandler) for h in logger.handlers)
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

    logger.info("start")
    logger.warning("warning-1")
    _flush_handlers(logger)

    module_logger = get_logger(name="arbolab.integration.module")
    module_logger.info("module-info")
    module_logger.error("module-error")
    _flush_handlers(module_logger)

    contents = first_log.read_text()
    assert "warning-1" in contents
    assert "module-error" in contents
    assert "start" not in contents
    assert "module-info" not in contents

    updated = config.with_updates(
        level="DEBUG",
        log_file_path=str(second_log),
        file_level="INFO",
        show_time=True,
    )
    logger = configure_logger(updated)
    logger.debug("debug-2")
    logger.info("info-2")
    _flush_handlers(logger)

    updated_contents = second_log.read_text()
    assert "info-2" in updated_contents
    assert "debug-2" not in updated_contents

    assert get_logger_config().name == "arbolab.integration"
