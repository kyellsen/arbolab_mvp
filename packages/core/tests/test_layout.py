"""Tests for workspace and results layouts."""

from __future__ import annotations

from pathlib import Path

import pytest
from arbolab.layout import ResultsLayout, WorkspaceLayout


def test_workspace_layout_paths_and_structure(tmp_path: Path) -> None:
    """Creates workspace layout paths and directory structure.

    Args:
        tmp_path: Temporary directory fixture.
    """
    layout = WorkspaceLayout(tmp_path)

    assert layout.root == tmp_path.resolve()
    assert layout.db_path == layout.root / "db" / "arbolab.duckdb"
    assert layout.config_path == layout.root / "config.yaml"
    assert layout.recipes_dir == layout.root / "recipes"
    assert layout.variants_dir == layout.root / "storage" / "variants"

    layout.ensure_structure()

    assert layout.db_path.parent.exists()
    assert layout.recipes_dir.exists()
    assert layout.variants_dir.exists()
    assert (layout.root / "logs").exists()
    assert (layout.root / "tmp").exists()


def test_results_layout_subdir_blocks_traversal(tmp_path: Path) -> None:
    """Blocks path traversal when creating result subdirectories.

    Args:
        tmp_path: Temporary directory fixture.
    """
    layout = ResultsLayout(tmp_path)

    safe_path = layout.subdir("plots")
    assert safe_path == tmp_path.resolve() / "plots"

    with pytest.raises(ValueError):
        layout.subdir("../escape")
