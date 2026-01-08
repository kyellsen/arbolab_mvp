"""Tests for WorkspaceDatabase behavior."""

from __future__ import annotations

from pathlib import Path

import pytest
from arbolab.database import WorkspaceDatabase
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
