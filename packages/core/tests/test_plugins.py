"""Tests for plugin discovery and registry behavior."""

from __future__ import annotations

import types
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pytest
from arbolab.plugins import PluginRegistry, PluginRuntime


@dataclass(frozen=True)
class DummyEntryPoint:
    """Minimal entry point stub for plugin discovery."""

    name: str
    loader: Callable[[], Any]

    def load(self) -> Any:
        """Load the plugin object.

        Returns:
            The loaded plugin object.
        """
        return self.loader()


def test_plugin_registry_discovers_enabled_plugins(monkeypatch: pytest.MonkeyPatch) -> None:
    """Loads enabled plugins and ignores missing or failing ones.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    def register(_: Any) -> None:
        """No-op register function for the plugin."""
        return None

    good_plugin = types.SimpleNamespace(register=register)

    def load_good() -> Any:
        """Load a valid plugin."""
        return good_plugin

    def load_bad() -> Any:
        """Raise an error for a broken plugin."""
        raise RuntimeError("boom")

    def load_skip() -> Any:
        """Load a disabled plugin."""
        return types.SimpleNamespace()

    entry_points = [
        DummyEntryPoint("good", load_good),
        DummyEntryPoint("bad", load_bad),
        DummyEntryPoint("skip", load_skip),
    ]

    def fake_entry_points(*, group: str) -> list[DummyEntryPoint]:
        """Return the stub entry points."""
        assert group == PluginRegistry.ENTRY_POINT_GROUP
        return entry_points

    monkeypatch.setattr("arbolab.plugins.importlib.metadata.entry_points", fake_entry_points)

    registry = PluginRegistry()
    registry.discover(["good", "bad"])

    assert registry.get_plugin("good") is good_plugin
    assert registry.get_plugin("bad") is None
    assert registry.get_plugin("skip") is None


def test_plugin_runtime_holds_registry() -> None:
    """Stores the registry reference in the runtime."""
    registry = PluginRegistry()
    runtime = PluginRuntime(registry)

    assert runtime.registry is registry


def test_plugin_runtime_initialization_handles_errors() -> None:
    """Handles plugins without register() and registration failures."""
    registry = PluginRegistry()
    called: dict[str, bool] = {"ok": False}

    def register(_: Any) -> None:
        """Record that the plugin was initialized."""
        called["ok"] = True

    def register_raises(_: Any) -> None:
        """Raise an error during plugin initialization."""
        raise RuntimeError("boom")

    registry._plugins = {
        "good": types.SimpleNamespace(register=register),
        "bad": types.SimpleNamespace(register=register_raises),
        "missing": types.SimpleNamespace(),
    }

    runtime = PluginRuntime(registry)
    runtime.initialize_plugins(object())

    assert called["ok"] is True
