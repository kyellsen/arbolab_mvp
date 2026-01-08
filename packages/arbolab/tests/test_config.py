"""Tests for LabConfig and config IO helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from arbolab.config import DEFAULT_CONFIG_FILENAME, LabConfig, create_default_config, load_config


def test_load_config_defaults_when_missing(tmp_path: Path) -> None:
    """Returns default config when config.yaml is missing.

    Args:
        tmp_path: Temporary directory fixture.
    """
    config = load_config(tmp_path)

    assert isinstance(config, LabConfig)
    assert config.input_path is None
    assert config.results_path is None
    assert config.enabled_plugins == []


def test_create_default_config_bootstraps_and_preserves_existing(tmp_path: Path) -> None:
    """Creates config.yaml once and leaves existing files untouched.

    Args:
        tmp_path: Temporary directory fixture.
    """
    input_root = tmp_path / "input"
    results_root = tmp_path / "results"

    config_path = create_default_config(tmp_path, initial_input=input_root, initial_results=results_root)
    assert config_path.exists()

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert data["input_path"] == str(input_root)
    assert data["results_path"] == str(results_root)

    sentinel = 'config_version: "9.9.9"\n'
    config_path.write_text(sentinel, encoding="utf-8")

    create_default_config(tmp_path, initial_input=input_root, initial_results=results_root)
    assert config_path.read_text(encoding="utf-8") == sentinel


def test_load_config_reads_values(tmp_path: Path) -> None:
    """Loads configured paths and plugins from config.yaml.

    Args:
        tmp_path: Temporary directory fixture.
    """
    config_path = tmp_path / DEFAULT_CONFIG_FILENAME
    payload = {
        "input_path": str(tmp_path / "input"),
        "results_path": str(tmp_path / "results"),
        "enabled_plugins": ["alpha", "beta"],
    }
    config_path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    config = load_config(tmp_path)
    assert config.input_path == payload["input_path"]
    assert config.results_path == payload["results_path"]
    assert config.enabled_plugins == ["alpha", "beta"]


def test_load_config_invalid_yaml_raises(tmp_path: Path) -> None:
    """Raises RuntimeError when config.yaml cannot be parsed.

    Args:
        tmp_path: Temporary directory fixture.
    """
    config_path = tmp_path / DEFAULT_CONFIG_FILENAME
    config_path.write_text("invalid: [", encoding="utf-8")

    with pytest.raises(RuntimeError):
        load_config(tmp_path)
