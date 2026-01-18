import pytest
from playwright.sync_api import Page, expect
from uuid import uuid4

from tests.e2e.pom.login_page import LoginPage
from tests.e2e.pom.explorer_page import ExplorerPage

@pytest.mark.e2e
def test_project_crud_flow(page: Page, server_url: str):
    """
    Test Scenario: Project CRUD (Create & Edit)
    """
    login_page = LoginPage(page, server_url)
    explorer_page = ExplorerPage(page, server_url)
    
    # 1. Login and go to Explorer
    login_page.login()
    explorer_page.navigate_to()
    
    # 2. Create Project
    explorer_page.click_new()
    explorer_page.modal.expect_visible()
    explorer_page.modal.expect_title("Create Project")
    
    # Test ESC key
    page.keyboard.press("Escape")
    explorer_page.modal.expect_hidden()
    
    # Re-open and create
    explorer_page.click_new()
    project_name = f"E2E-Project-{uuid4().hex[:6]}"
    description = "Created by Playwright POM"
    
    explorer_page.modal.fill_input("name", project_name)
    explorer_page.modal.fill_textarea("description", description)
    explorer_page.modal.submit()
    
    explorer_page.modal.expect_hidden()
    explorer_page.expect_in_list(project_name)
    
    # 3. Edit via Table
    explorer_page.click_row_edit(project_name)
    explorer_page.modal.expect_visible()
    explorer_page.modal.expect_title("Edit Project")
    explorer_page.modal.cancel()
    explorer_page.modal.expect_hidden()
    
    # 4. Edit via Inspector
    explorer_page.select_row(project_name)
    explorer_page.inspector.expect_content(project_name)
    explorer_page.inspector.expect_content(description)
    
    explorer_page.inspector.click_edit()
    explorer_page.modal.expect_visible()
    
    updated_name = f"{project_name}-Updated"
    explorer_page.modal.fill_input("name", updated_name)
    explorer_page.modal.submit()
    
    explorer_page.modal.expect_hidden()
    explorer_page.inspector.expect_content(updated_name)
    explorer_page.expect_in_list(updated_name)
    
    # 5. Cleanup (Delete)
    explorer_page.inspector.click_delete()
    explorer_page.inspector.expect_content("Select an item")
    explorer_page.expect_not_in_list(updated_name)


@pytest.mark.e2e
def test_create_thing(page: Page, server_url: str):
    """Test creating a Thing entity."""
    login_page = LoginPage(page, server_url)
    explorer_page = ExplorerPage(page, server_url)

    login_page.login()
    explorer_page.navigate_to()

    # Switch category (assuming "Things" exists)
    explorer_page.select_category("Things")
    explorer_page.click_new()
    
    explorer_page.modal.expect_visible()
    explorer_page.modal.expect_title("Create Thing")
    
    # Verify specific field exists (simplified check)
    expect(page.locator("input[name='kind']")).to_be_visible()


@pytest.mark.e2e
def test_create_sensor(page: Page, server_url: str):
    """Test creating a Sensor entity."""
    login_page = LoginPage(page, server_url)
    explorer_page = ExplorerPage(page, server_url)

    login_page.login()
    explorer_page.navigate_to()

    explorer_page.select_category("Sensors")
    explorer_page.click_new()
    
    explorer_page.modal.expect_visible()
    explorer_page.modal.expect_title("Create Sensor")
    
    expect(page.locator("input[name='sensor_model_id']")).to_be_visible()
