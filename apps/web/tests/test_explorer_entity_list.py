from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


@dataclass(slots=True)
class DummyEntity:
    """Minimal entity used to render the explorer list template."""

    id: int
    name: str
    updated_at: datetime | None


class EntityListTemplateParser(HTMLParser):
    """Collect row and button attributes from rendered HTML."""

    def __init__(self) -> None:
        """Initialize the parser with attribute collections."""
        super().__init__()
        self.rows: list[dict[str, str | None]] = []
        self.buttons: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record row and button attributes for later assertions."""
        attr_map = {name: value for name, value in attrs}
        if tag == "tr":
            self.rows.append(attr_map)
        elif tag == "button":
            self.buttons.append(attr_map)


def render_entity_list(entity_type: str, entities: list[DummyEntity]) -> str:
    """Render the explorer entity list template for testing."""
    base_dir = Path(__file__).resolve().parents[1]
    templates_dir = base_dir / "templates"
    env = Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=True)
    template = env.get_template("partials/entity_list.html")
    return template.render(entity_type=entity_type, entities=entities)


def test_entity_row_click_opens_inspector_sidebar() -> None:
    """Ensure list rows open the inspector while action buttons stop propagation."""
    html = render_entity_list(
        "project",
        [DummyEntity(id=1, name="Project Alpha", updated_at=datetime(2024, 1, 1))],
    )

    parser = EntityListTemplateParser()
    parser.feed(html)

    row = next(
        (
            attrs
            for attrs in parser.rows
            if attrs.get("hx-get") == "/explorer-ui/inspector/project/1"
        ),
        None,
    )
    assert row is not None
    assert row.get("hx-target") == "#explorer-inspector-panel"
    assert row.get("hx-swap") == "innerHTML"

    edit_button = next(
        (attrs for attrs in parser.buttons if attrs.get("title") == "Edit"),
        None,
    )
    assert edit_button is not None
    assert "@click.stop" in edit_button
    assert edit_button.get("hx-get") == "/explorer-ui/form/project?entity_id=1"

    delete_button = next(
        (attrs for attrs in parser.buttons if attrs.get("title") == "Delete"),
        None,
    )
    assert delete_button is not None
    assert "@click.stop" in delete_button
    assert delete_button.get("hx-delete") == "/api/entities/project/1"
