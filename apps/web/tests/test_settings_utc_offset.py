"""Tests for the user UTC offset UI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
TEMPLATES = Jinja2Templates(directory=str(TEMPLATES_DIR))


@dataclass(frozen=True)
class DummyUser:
    """Minimal user stub for template rendering."""

    email: str
    utc_offset_minutes: int | None = None


def render_template(template_name: str, context: dict[str, Any]) -> str:
    """Render a template with the provided context."""
    return TEMPLATES.get_template(template_name).render(context)


def test_profile_form_renders_utc_offset_fields() -> None:
    """Profile form includes the UTC offset inputs and helpers."""
    html = render_template(
        "settings/partials/profile_form.html",
        {"user": DummyUser(email="user@example.com", utc_offset_minutes=90)},
    )

    assert 'name="utc_offset_sign"' in html
    assert 'name="utc_offset_hours"' in html
    assert 'name="utc_offset_minutes"' in html
    assert "data-utc-offset-hours" in html
    assert "data-utc-offset-minutes" in html
    assert 'value="1"' in html
    assert 'value="30"' in html
    assert "data-utc-offset-detected" in html


def test_base_template_exposes_utc_offset() -> None:
    """Base template includes the selected UTC offset attribute."""
    html = render_template(
        "base.html",
        {
            "user": DummyUser(email="user@example.com", utc_offset_minutes=90),
            "plugin_nav": [],
            "current_workspace": None,
            "all_workspaces": [],
        },
    )

    assert 'data-utc-offset-minutes="90"' in html
