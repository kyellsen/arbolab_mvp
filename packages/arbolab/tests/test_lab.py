"""Tests for the Lab entry point and workspace lifecycle."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from arbolab.lab import Lab
from sqlalchemy import text


def _patch_empty_entry_points(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace entry point discovery with an empty list.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """

    def fake_entry_points(*, group: str) -> list[Any]:
        """Return no entry points for discovery."""
        return []

    monkeypatch.setattr("arbolab.plugins.importlib.metadata.entry_points", fake_entry_points)


def test_lab_open_bootstraps_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Bootstraps config and initializes layout, database, and store.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    _patch_empty_entry_points(monkeypatch)

    workspace_root = tmp_path / "workspace"
    input_root = tmp_path / "input"
    results_root = tmp_path / "results"

    lab = Lab.open(workspace_root=workspace_root, input_root=input_root, results_root=results_root)

    assert (workspace_root / "config.yaml").exists()
    assert lab.layout.root == workspace_root.resolve()
    assert lab.results.root == results_root.resolve()
    assert lab.input_root == input_root.resolve()
    assert lab.layout.db_path.parent.exists()
    assert lab.layout.variants_dir.exists()
    assert lab.layout.recipes_dir.exists()

    with lab.database.session() as session:
        result = session.execute(text("select 1")).fetchone()
        assert result is not None
        assert result[0] == 1


def test_lab_open_uses_config_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Restores input and results roots from config.yaml.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    _patch_empty_entry_points(monkeypatch)

    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()

    input_root = tmp_path / "input_cfg"
    results_root = tmp_path / "results_cfg"

    payload = {"input_path": str(input_root), "results_path": str(results_root), "enabled_plugins": []}
    (workspace_root / "config.yaml").write_text(yaml.safe_dump(payload), encoding="utf-8")

    lab = Lab.open(workspace_root=workspace_root, input_root=None, results_root=None)

    assert lab.input_root == input_root.resolve()
    assert lab.results.root == results_root.resolve()
    assert results_root.exists()


def test_lab_open_with_base_root_derives_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Derives input and results roots from base_root when omitted.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    _patch_empty_entry_points(monkeypatch)

    base_root = tmp_path / "base"
    workspace_root = base_root / "workspace"

    lab = Lab.open(workspace_root=workspace_root, input_root=None, results_root=None, base_root=base_root)

    assert lab.layout.root == workspace_root.resolve()
    assert lab.input_root == (base_root / "input").resolve()
    assert lab.results.root == (base_root / "results").resolve()


def test_lab_run_recipe_missing_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Raises when recipe file is missing.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    _patch_empty_entry_points(monkeypatch)

    lab = Lab.open(workspace_root=tmp_path / "workspace")

    with pytest.raises(FileNotFoundError):
        lab.run_recipe(tmp_path / "missing.json")


def test_lab_run_recipe_existing_succeeds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Runs recipe when the file exists.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    _patch_empty_entry_points(monkeypatch)

    lab = Lab.open(workspace_root=tmp_path / "workspace")
    recipe_path = lab.layout.recipe_path()
    recipe_path.write_text('{"recipe_version": "1.0.0", "steps": []}', encoding="utf-8")

    lab.run_recipe(recipe_path)


def test_lab_open_with_base_root_and_missing_workspace_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Derives workspace root when base_root is set and workspace_root is None.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    _patch_empty_entry_points(monkeypatch)

    base_root = tmp_path / "base"

    lab = Lab.open(workspace_root=None, base_root=base_root)

    assert lab.layout.root == (base_root / "workspace").resolve()


def test_lab_open_defaults_results_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Falls back to workspace/results when results root is not configured.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    _patch_empty_entry_points(monkeypatch)

    workspace_root = tmp_path / "workspace"
    input_root = tmp_path / "input"

    lab = Lab.open(workspace_root=workspace_root, input_root=input_root, results_root=None)

    assert lab.results.root == (workspace_root / "results").resolve()
    assert (workspace_root / "results").exists()


def test_lab_run_recipe_default_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Runs recipe from the default workspace path when no path is provided.

    Args:
        tmp_path: Temporary directory fixture.
        monkeypatch: Pytest monkeypatch fixture.
    """
    _patch_empty_entry_points(monkeypatch)

    lab = Lab.open(workspace_root=tmp_path / "workspace")
    recipe_path = lab.layout.recipe_path()
    recipe_path.write_text('{"recipe_version": "1.0.0", "steps": []}', encoding="utf-8")

    lab.run_recipe()
