"""Tests for domain entity CRUD logic."""

from __future__ import annotations

import pytest
from arbolab.models import Base, Project
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.fixture
def session():
    """Returns an in-memory DuckDB session for testing."""
    engine = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_crud_create(session: Session) -> None:
    """Test creating an entity."""
    project = Project.create(session, name="Test Project")
    session.flush()
    assert project.id is not None
    assert project.name == "Test Project"


def test_crud_get(session: Session) -> None:
    """Test getting an entity by ID."""
    project = Project.create(session, name="Test Project")
    session.flush()

    fetched = Project.get(session, project.id)
    assert fetched is not None
    assert fetched.id == project.id
    assert fetched.name == "Test Project"


def test_crud_update(session: Session) -> None:
    """Test updating an entity."""
    project = Project.create(session, name="Old Name")
    session.flush()

    project.update(session, name="New Name")
    session.flush()

    assert project.name == "New Name"
    # Verify persistence
    session.expire(project)
    assert project.name == "New Name"


def test_crud_delete(session: Session) -> None:
    """Test deleting an entity."""
    project = Project.create(session, name="To Delete")
    session.flush()
    pid = project.id

    project.delete(session)
    session.flush()

    assert Project.get(session, pid) is None


def test_view_representation(session: Session) -> None:
    """Test string representations."""
    # Case 1: With name
    p1 = Project(name="MyProject")
    session.add(p1)
    session.flush()

    assert str(p1) == "MyProject"
    assert "MyProject" in repr(p1)
    assert "Project" in repr(p1)
    assert f"id={p1.id}" in repr(p1)

    # Case 2: Without name (transient or no name field)
    # Project has optional name, let's try one without
    p2 = Project()
    session.add(p2)
    session.flush()
    # Fallback for str usually classes name + id
    assert str(p2) == f"Project #{p2.id}"

    # Transient
    p3 = Project(name="Transient")
    assert "transient" in repr(p3)


def test_export_to_dict(session: Session) -> None:
    """Test dictionary export."""
    project = Project.create(session, name="ExportMe", description="Desc")
    session.flush()

    data = project.to_dict()
    assert isinstance(data, dict)
    assert data["name"] == "ExportMe"
    assert data["description"] == "Desc"
    assert data["id"] == project.id
    # Check that it includes mixin fields
    assert "created_at" in data
    assert "updated_at" in data
