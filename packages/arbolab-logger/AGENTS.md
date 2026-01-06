# AGENTS.md – Logger Package (`arbolab-logger`)

## Purpose & Scope
This package contains the reusable logging helpers used across the ArboLab
monorepo. It exposes a small API (`LoggerConfig`, `configure_logger`,
`get_logger`, `get_logger_config`) that the core (`arbolab`) and plugins import
when they need a configured logger instance. The package focuses on producing
consistent, human-friendly output for both terminals and notebook environments
by delegating the rendering to **Rich**.

## API Surface
- `arbolab_logger.LoggerConfig`: frozen pydantic model describing log behaviour.
- `arbolab_logger.configure_logger()`: activates a logger according to the
  provided config and returns the resulting `logging.Logger` instance.
- `arbolab_logger.get_logger()`: convenience accessor that returns a configured
  logger, optionally for a custom name.
- `arbolab_logger.get_logger_config()`: exposes the currently active config
  instance for inspection.

## Responsibilities
- Provide a deterministic scheme for configuring log levels, formatting, Rich
  features (tracebacks, markup, linking), and colour usage.
- Use Rich's `Console` and `RichHandler` to ensure attractive output in
  terminals and notebooks without implementing custom ANSI handling.
- Remain state-free apart from the immutable config snapshot stored in an
  internal module-level dictionary so that the core can safely reconfigure the
  logger during Lab bootstrap.
- Offer extension points via the config model instead of implicit globals.

## Limitations / Forbidden Areas
- This package does **not** implement business logic, persistence, or plugin
  interfaces—its sole concern is logging.
- File output is opt-in only. By default the logger writes only to stdout/stderr
  and remains side-effect free. When `log_to_file` is enabled, the logger may
  write to the configured log file path.
- The module must stay free of device-specific knowledge and must not depend on
  any other package inside the monorepo to avoid circular imports.
- The Rich handler is the only supported output backend; do not introduce custom
  colour codes or TTY detection outside of Rich.

## Testing
- All tests reside in `packages/arbolab-logger/tests` and are executed via the
  workspace `pytest` invocation from the repository root.
- Tests must create temporary configs and never modify global logging state
  outside their scope. Pytest automatically resets handlers between tests.

## Versioning / Migrations
- Schema changes to `LoggerConfig` follow semantic versioning. Breaking
  modifications (field removals, renamed options) require a major version bump.
- The config model is declared as frozen so that any potential runtime migration
  happens by constructing a new instance and calling
  `configure_logger(new_config)`; no in-place mutation is allowed.
