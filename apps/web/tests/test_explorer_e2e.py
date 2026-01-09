"""Browser tests for the Explorer UI."""

from __future__ import annotations

from uuid import uuid4

from playwright.sync_api import Page, expect


def login(page: Page, server_url: str) -> None:
    """Log in using seeded credentials.

    Args:
        page: Playwright page instance.
        server_url: Base URL for the server.
    """
    page.goto(f"{server_url}/auth/login")
    page.fill("input[name='username']", "mail@kyell.de")
    page.fill("input[name='password']", "123")
    page.click("button[type='submit']")
    page.wait_for_url(f"{server_url}/")


def open_explorer(page: Page) -> None:
    """Open the Explorer via the sidebar to exercise HTMX swapping.

    Args:
        page: Playwright page instance.
    """
    page.locator("a[data-nav-path='/explorer']").click()
    page.wait_for_selector("#entity-list-container")


def click_new_button(page: Page) -> None:
    """Click the Explorer header New button.

    Args:
        page: Playwright page instance.
    """
    page.locator("#main-stage button", has_text="New").first.click()


def test_new_button_opens_thing_form(page: Page, server_url: str) -> None:
    """Opens the thing create form when Things is the active category."""
    login(page, server_url)
    open_explorer(page)

    page.get_by_role("button", name="Things").click()
    click_new_button(page)

    modal = page.locator("#modal-container")
    expect(modal).to_contain_text("Create Thing")
    expect(modal.locator("input[name='kind']")).to_be_visible()


def test_new_button_opens_sensor_form(page: Page, server_url: str) -> None:
    """Opens the sensor create form when Sensors is the active category."""
    login(page, server_url)
    open_explorer(page)

    page.get_by_role("button", name="Sensors").click()
    click_new_button(page)

    modal = page.locator("#modal-container")
    expect(modal).to_contain_text("Create Sensor")
    expect(modal.locator("input[name='sensor_model_id']")).to_be_visible()


def test_delete_action_removes_entity_and_resets_inspector(page: Page, server_url: str) -> None:
    """Deletes a project and clears the inspector selection."""
    login(page, server_url)
    open_explorer(page)

    project_name = f"Test Project {uuid4().hex[:8]}"

    click_new_button(page)
    page.fill("#modal-container input[name='name']", project_name)
    page.get_by_role("button", name="Create Entity").click()

    expect(page.locator("#modal-container form")).to_have_count(0)
    expect(page.locator("#entity-list-container")).to_contain_text(project_name)

    row = page.locator("tr", has_text=project_name)
    row.click()
    expect(page.locator("#explorer-inspector-panel")).to_contain_text(project_name)

    row.locator("button[title='Delete']").click()
    expect(page.locator("#explorer-inspector-panel")).to_contain_text(
        "Select an item to view details"
    )
    expect(page.locator("#entity-list-container")).not_to_contain_text(project_name)
