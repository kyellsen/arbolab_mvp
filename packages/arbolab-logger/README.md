# Arbolab Logger (`arbolab-logger`)

Rich-based logging helpers for the Arbolab Lab runtime. It provides consistent, human-friendly output for both terminals and notebook environments.

## Purpose & Scope
This package contains reusable logging helpers used across the ArboLab monorepo. It focuses on producing attractive output by delegating the rendering to **Rich**.

## API Surface
- `arbolab_logger.LoggerConfig`: Frozen Pydantic model describing logging behavior.
- `arbolab_logger.configure_logger()`: Activates a logger according to the provided config.
- `arbolab_logger.get_logger()`: Convenience accessor that returns a configured logger.
- `arbolab_logger.get_logger_config()`: Exposes the currently active config instance.

## Responsibilities
- Provide a deterministic scheme for log levels, formatting, and Rich features (tracebacks, markup, linking).
- Use Rich's `Console` and `RichHandler` for consistent output.
- Remain state-free (module-level immutable config snapshot).

## Limitations
- No business logic or persistence—sole concern is logging.
- No device-specific knowledge.
- Must not depend on any other package inside the monorepo (prevents circular imports).

## Development
Tests reside in `tests/` and can be run via `pytest`.
