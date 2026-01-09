"""Tests for WorkspaceDatabase behavior."""

from __future__ import annotations

from pathlib import Path

import pytest
from arbolab.database import WorkspaceDatabase
from arbolab.models import Base
from sqlalchemy import text


def test_workspace_database_connect_and_session(tmp_path: Path) -> None:
    """Creates the engine and supports session execution.

    Args:
        tmp_path: Temporary directory fixture.
    """
    db_path = tmp_path / "db" / "arbolab.duckdb"
    database = WorkspaceDatabase(db_path)

    database.connect()

    assert db_path.parent.exists()

    with database.session() as session:
        result = session.execute(text("select 1")).fetchone()
        assert result is not None
        assert result[0] == 1


def test_workspace_database_session_rolls_back(tmp_path: Path) -> None:
    """Rolls back and re-raises exceptions from the session context.

    Args:
        tmp_path: Temporary directory fixture.
    """
    database = WorkspaceDatabase(tmp_path / "db" / "arbolab.duckdb")
    database.connect()

    with pytest.raises(RuntimeError):
        with database.session() as session:
            session.execute(text("select 1"))
            raise RuntimeError("boom")


def test_workspace_database_get_native_con(tmp_path: Path) -> None:
    """Provides a native duckdb connection for analytics.

    Args:
        tmp_path: Temporary directory fixture.
    """
    database = WorkspaceDatabase(tmp_path / "db" / "arbolab.duckdb")

    con = database.get_native_con()
    try:
        value = con.execute("select 1").fetchone()[0]
        assert value == 1
    finally:
        con.close()


def test_workspace_database_engine_property_reuses_connection(tmp_path: Path) -> None:
    """Creates the engine lazily and avoids reconnecting on second call.

    Args:
        tmp_path: Temporary directory fixture.
    """
    database = WorkspaceDatabase(tmp_path / "db" / "arbolab.duckdb")

    engine = database.engine
    assert engine is database.engine

    database.connect()


def test_workspace_database_session_bootstraps_connection(tmp_path: Path) -> None:
    """Creates a session without an explicit connect call.

    Args:
        tmp_path: Temporary directory fixture.
    """
    database = WorkspaceDatabase(tmp_path / "db" / "arbolab.duckdb")

    with database.session() as session:
        result = session.execute(text("select 1")).fetchone()
        assert result is not None
        assert result[0] == 1


def test_workspace_database_ensure_schema_creates_namespace(tmp_path: Path) -> None:
    """Ensures custom schemas are created when missing.

    Args:
        tmp_path: Temporary directory fixture.
    """
    database = WorkspaceDatabase(tmp_path / "db" / "arbolab.duckdb")

    database.ensure_schema("custom")

    with database.session() as session:
        schemas = session.execute(text("select schema_name from information_schema.schemata")).fetchall()
        assert "custom" in {row[0] for row in schemas}


def test_workspace_database_create_tables_connects(tmp_path: Path) -> None:
    """Creates tables and connects when called before connect().

    Args:
        tmp_path: Temporary directory fixture.
    """
    database = WorkspaceDatabase(tmp_path / "db" / "arbolab.duckdb")

    database.create_tables(Base.metadata)

    with database.session() as session:
        result = session.execute(text("select 1")).fetchone()
        assert result is not None


def test_workspace_database_logs_after_flush(tmp_path: Path) -> None:
    """Executes the post-flush logging hook.

    Args:
        tmp_path: Temporary directory fixture.
    """
    class DummySession:
        """Session stub with new/dirty/deleted lists."""

        def __init__(self) -> None:
            self.new = [object()]
            self.dirty = [object()]
            self.deleted = [object()]

    database = WorkspaceDatabase(tmp_path / "db" / "arbolab.duckdb")
    database._log_after_flush(DummySession(), None)
