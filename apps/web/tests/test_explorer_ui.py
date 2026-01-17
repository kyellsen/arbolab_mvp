"""Tests for explorer UI behaviors."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from arbolab.lab import Lab
from fastapi.templating import Jinja2Templates

from apps.web.core.domain import ENTITY_MAP, delete_entity, get_entity, list_entities

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
TEMPLATES = Jinja2Templates(directory=str(TEMPLATES_DIR))


@dataclass(frozen=True)
class DummyEntity:
    """Minimal entity stub for template rendering."""

    id: int
    name: str
    updated_at: datetime | None = None


def render_template(template_name: str, context: dict[str, Any]) -> str:
    """Render a template with the provided context.

    Args:
        template_name: Template path relative to the templates directory.
        context: Template context to render.

    Returns:
        Rendered HTML.
    """
    return TEMPLATES.get_template(template_name).render(context)


def fields_for_entity(entity_type: str) -> Mapping[str, Any]:
    """Return schema fields for an entity type.

    Args:
        entity_type: Entity identifier from the explorer.

    Returns:
        Schema field mapping for template rendering.
    """
    schema = ENTITY_MAP[entity_type]["schema"]
    return schema.model_fields if hasattr(schema, "model_fields") else schema.__fields__


def render_explorer_content(active_entity: str) -> str:
    """Render the explorer content partial for a given active entity.

    Args:
        active_entity: Entity type selected in the explorer.

    Returns:
        Rendered explorer content HTML.
    """
    return render_template(
        "partials/explorer_content.html",
        {
            "active_entity": active_entity,
            "open_form_entity": None,
        },
    )


def render_modal_form(entity_type: str) -> str:
    """Render the modal form partial for an entity type.

    Args:
        entity_type: Entity identifier from the explorer.

    Returns:
        Rendered modal form HTML.
    """
    return render_template(
        "partials/modal_form.html",
        {
            "entity_type": entity_type,
            "entity": None,
            "fields": fields_for_entity(entity_type),
            "redirect_url": None,
        },
    )


def test_explorer_new_button_targets_thing_form() -> None:
    """Opens the thing create form when the explorer targets things."""
    html = render_explorer_content("thing")

    assert "x-data=\"{ activeEntity: 'thing' }\"" in html
    assert 'hx-get="/explorer-ui/form/thing"' in html
    assert ":hx-get=\"'/explorer-ui/form/' + activeEntity\"" in html

    form_html = render_modal_form("thing")

    assert "Create Thing" in form_html
    assert 'name="kind"' in form_html


def test_explorer_new_button_targets_sensor_form() -> None:
    """Opens the sensor create form when the explorer targets sensors."""
    html = render_explorer_content("sensor")

    assert "x-data=\"{ activeEntity: 'sensor' }\"" in html
    assert 'hx-get="/explorer-ui/form/sensor"' in html
    assert ":hx-get=\"'/explorer-ui/form/' + activeEntity\"" in html

    form_html = render_modal_form("sensor")

    assert "Create Sensor" in form_html
    assert 'name="sensor_model_id"' in form_html


def test_delete_action_removes_entity_and_resets_inspector(tmp_path: Path) -> None:
    """Deletes an entity and ensures the inspector reset hook is present."""
    lab = Lab.open(
        workspace_root=tmp_path / "workspace",
        input_root=tmp_path / "input",
        results_root=tmp_path / "results",
    )

    project = lab.define_project(name="Test Project")
    sensor_model = lab.define_sensor_model(name="Test Sensor Model")
    sensor = lab.define_sensor(
        name="Test Sensor",
        project_id=project.id,
        sensor_model_id=sensor_model.id,
    )

    with lab.database.session() as session:
        asyncio.run(delete_entity(session, "sensor", sensor.id, lab=lab))

    with lab.database.session() as session:
        deleted = asyncio.run(get_entity(session, "sensor", sensor.id))
        assert deleted is None
        sensors = asyncio.run(list_entities(session, "sensor"))
        assert all(item.id != sensor.id for item in sensors)

    list_html = render_template(
        "partials/entity_list.html",
        {
            "entity_type": "sensor",
            "entities": [DummyEntity(id=1, name="Temp Sensor")],
        },
    )

    assert 'hx-delete="/api/entities/sensor/1"' in list_html
    assert "htmx.ajax('GET','/explorer-ui/list/sensor','#entity-list-container');" in list_html
    assert "Select an item to view details" in list_html


def test_inspector_renders_missing_entity_message() -> None:
    """Shows a not-found message when the inspector receives no entity."""
    html = render_template(
        "partials/inspector.html",
        {
            "entity_type": "sensor_model",
            "entity": None,
            "relations": {"parents": [], "children": []},
            "relation_exclude_keys": [],
        },
    )

    assert "Entity not found." in html
