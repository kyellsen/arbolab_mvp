"""Tests for settings UI tab highlighting behavior."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
TEMPLATES = Jinja2Templates(directory=str(TEMPLATES_DIR))


@dataclass(frozen=True)
class DummyUser:
    """Minimal user stub for template rendering."""

    email: str = "user@example.com"
    full_name: str | None = None
    organization: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    zip_code: str | None = None
    country: str | None = None


def render_template(template_name: str, context: dict[str, Any]) -> str:
    """Render a template with the provided context.

    Args:
        template_name: Template path relative to the templates directory.
        context: Template context to render.

    Returns:
        Rendered HTML.
    """
    return TEMPLATES.get_template(template_name).render(context)


def render_user_settings_content(active_tab: str) -> str:
    """Render the user settings partial for a given active tab.

    Args:
        active_tab: Active tab identifier ("profile" or "security").

    Returns:
        Rendered HTML.
    """
    return render_template(
        "settings/partials/user_settings_content.html",
        {"active_tab": active_tab, "user": DummyUser()},
    )


def extract_button_classes(html: str, hx_get: str) -> str:
    """Extract the class attribute for a button with the given hx-get.

    Args:
        html: Rendered HTML content.
        hx_get: Value of the hx-get attribute to match.

    Returns:
        The class attribute value for the matching button.
    """
    pattern = rf'hx-get="{re.escape(hx_get)}"[^>]*class="([^"]+)"'
    match = re.search(pattern, html, re.S)
    if not match:
        raise AssertionError(f"Button with hx-get {hx_get!r} not found.")
    return match.group(1)


def test_settings_security_tab_marks_security_active() -> None:
    """Marks the security tab as active when the security section renders."""
    html = render_user_settings_content("security")

    assert 'id="settings-shell"' in html
    assert 'hx-target="#settings-shell"' in html
    assert 'hx-swap="outerHTML"' in html

    security_classes = extract_button_classes(html, "/settings/security")
    assert "bg-slate-800" in security_classes
    assert "text-emerald-400" in security_classes
    assert "hover:text-white" not in security_classes

    profile_classes = extract_button_classes(html, "/settings/")
    assert "text-slate-400" in profile_classes
    assert "hover:bg-slate-800" in profile_classes
    assert "hover:text-white" in profile_classes
