"""Unit tests for MetadataImporter edge cases and branches."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import polars as pl
import pytest
from arbolab.models import Base, Project, SensorModel
from arbolab.services.importer import MetadataImporter
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def _write_csv(path: Path, data: dict[str, list[Any]]) -> None:
    """Write a small CSV using polars.

    Args:
        path: Destination file path.
        data: Column data mapping.
    """
    pl.DataFrame(data).write_csv(path)


def test_import_package_rejects_invalid_path(tmp_path: Path) -> None:
    """Raises when the package path is missing or misnamed.

    Args:
        tmp_path: Temporary directory fixture.
    """
    engine = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(engine)
    importer = MetadataImporter(engine)

    invalid_path = tmp_path / "package.json"
    invalid_path.write_text("{}", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        importer.import_package(invalid_path)


def test_import_package_imports_all_resources(tmp_path: Path) -> None:
    """Imports a full metadata package with all supported resources.

    Args:
        tmp_path: Temporary directory fixture.
    """
    engine = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(SensorModel(id=1, name="Model"))
        session.commit()

    importer = MetadataImporter(engine)
    pkg_dir = tmp_path / "metadata"
    pkg_dir.mkdir(parents=True)

    _write_csv(pkg_dir / "projects.csv", {"id": [1], "name": ["Project"]})
    _write_csv(
        pkg_dir / "things.csv",
        {"id": [10], "project_id": [1], "kind": ["tree"], "name": ["Thing"]},
    )
    _write_csv(
        pkg_dir / "treatments.csv",
        {"id": [20], "project_id": [1], "name": ["Treatment"]},
    )
    _write_csv(
        pkg_dir / "experiments.csv",
        {"id": [30], "project_id": [1], "name": ["Experiment"]},
    )
    _write_csv(
        pkg_dir / "experimental_units.csv",
        {"id": [40], "project_id": [1], "thing_id": [10], "name": ["Unit"]},
    )
    _write_csv(
        pkg_dir / "sensors.csv",
        {"id": [50], "project_id": [1], "sensor_model_id": [1], "name": ["Sensor"]},
    )
    _write_csv(
        pkg_dir / "sensor_deployments.csv",
        {
            "id": [60],
            "experiment_id": [30],
            "experimental_unit_id": [40],
            "sensor_id": [50],
            "start_time": ["2026-01-01T00:00:00"],
        },
    )

    datapackage = {
        "name": "full-package",
        "resources": [
            {"name": "projects", "path": "projects.csv"},
            {"name": "things", "path": "things.csv"},
            {"name": "treatments", "path": "treatments.csv"},
            {"name": "experiments", "path": "experiments.csv"},
            {"name": "experimental_units", "path": "experimental_units.csv"},
            {"name": "sensors", "path": "sensors.csv"},
            {"name": "sensor_deployments", "path": "sensor_deployments.csv"},
        ],
    }

    pkg_file = pkg_dir / "datapackage.json"
    pkg_file.write_text(json.dumps(datapackage), encoding="utf-8")

    stats = importer.import_package(pkg_file)

    assert stats["projects"]["count"] == 1
    assert stats["things"]["count"] == 1
    assert stats["treatments"]["count"] == 1
    assert stats["experiments"]["count"] == 1
    assert stats["experimental_units"]["count"] == 1
    assert stats["sensors"]["count"] == 1
    assert stats["sensor_deployments"]["count"] == 1


def test_import_resource_skips_without_path(tmp_path: Path) -> None:
    """Skips resources that have no path defined.

    Args:
        tmp_path: Temporary directory fixture.
    """
    engine = create_engine("duckdb:///:memory:")
    importer = MetadataImporter(engine)

    result = importer._import_resource(tmp_path, {"name": "projects"}, Project)

    assert result["status"] == "skipped"


def test_import_resource_missing_file(tmp_path: Path) -> None:
    """Returns missing_file when the CSV does not exist.

    Args:
        tmp_path: Temporary directory fixture.
    """
    engine = create_engine("duckdb:///:memory:")
    importer = MetadataImporter(engine)

    result = importer._import_resource(
        tmp_path,
        {"name": "projects", "path": "missing.csv"},
        Project,
    )

    assert result["status"] == "missing_file"


def test_import_resource_handles_read_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Returns error when CSV cannot be parsed.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    engine = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(engine)
    importer = MetadataImporter(engine)

    csv_path = tmp_path / "projects.csv"
    csv_path.write_text("id,name\n1,Test\n", encoding="utf-8")

    def raise_read(_: Path) -> Any:
        """Raise a parsing error."""
        raise RuntimeError("boom")

    monkeypatch.setattr("arbolab.services.importer.pl.read_csv", raise_read)

    result = importer._import_resource(
        tmp_path,
        {"name": "projects", "path": "projects.csv"},
        Project,
    )

    assert result["status"] == "error"


def test_import_resource_returns_empty_status(tmp_path: Path) -> None:
    """Returns empty status when CSV has no rows.

    Args:
        tmp_path: Temporary directory fixture.
    """
    engine = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(engine)
    importer = MetadataImporter(engine)

    csv_path = tmp_path / "projects.csv"
    _write_csv(csv_path, {"id": [], "name": []})

    result = importer._import_resource(
        tmp_path,
        {"name": "projects", "path": "projects.csv"},
        Project,
    )

    assert result["status"] == "empty"


def test_import_resource_returns_no_valid_fields(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Returns no_valid_fields when rows have no usable columns.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    engine = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(engine)
    importer = MetadataImporter(engine)

    csv_path = tmp_path / "projects.csv"
    csv_path.write_text("id,name\n1,Test\n", encoding="utf-8")

    class DummyFrame:
        """Frame stub with empty dict output."""

        def is_empty(self) -> bool:
            """Report non-empty to reach the column filter."""
            return False

        def to_dicts(self) -> list[dict[str, Any]]:
            """Return no records after conversion."""
            return []

    monkeypatch.setattr("arbolab.services.importer.pl.read_csv", lambda _: DummyFrame())

    result = importer._import_resource(
        tmp_path,
        {"name": "projects", "path": "projects.csv"},
        Project,
    )

    assert result["status"] == "no_valid_fields"


def test_import_resource_sqlite_upsert_updates(tmp_path: Path) -> None:
    """Uses sqlite on_conflict updates when id is present.

    Args:
        tmp_path: Temporary directory fixture.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    importer = MetadataImporter(engine)

    csv_path = tmp_path / "projects.csv"
    resource = {"name": "projects", "path": "projects.csv"}

    _write_csv(csv_path, {"id": [1], "name": ["Initial"]})
    first = importer._import_resource(tmp_path, resource, Project)
    assert first["count"] == 1

    _write_csv(csv_path, {"id": [1], "name": ["Updated"]})
    importer._import_resource(tmp_path, resource, Project)

    with Session(engine) as session:
        project = session.get(Project, 1)
        assert project is not None
        assert project.name == "Updated"


def test_import_resource_sqlite_upsert_noop_for_id_only(tmp_path: Path) -> None:
    """Uses on_conflict_do_nothing when only id is present.

    Args:
        tmp_path: Temporary directory fixture.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    importer = MetadataImporter(engine)

    csv_path = tmp_path / "projects.csv"
    _write_csv(csv_path, {"id": [2]})

    result = importer._import_resource(
        tmp_path,
        {"name": "projects", "path": "projects.csv"},
        Project,
    )

    assert result["count"] == 1


def test_import_resource_reports_upsert_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Returns error status when the database insert fails.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    importer = MetadataImporter(engine)

    csv_path = tmp_path / "projects.csv"
    _write_csv(csv_path, {"id": [3], "name": ["Broken"]})

    def raise_execute(self: Session, *_args: Any, **_kwargs: Any) -> Any:
        """Raise an error during execution."""
        raise RuntimeError("boom")

    monkeypatch.setattr("arbolab.services.importer.Session.execute", raise_execute)

    result = importer._import_resource(
        tmp_path,
        {"name": "projects", "path": "projects.csv"},
        Project,
    )

    assert result["status"] == "error"
