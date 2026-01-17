import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_explorer_crud_flow(page: Page):
    """
    Test Scenario: Explorer CRUD (Create & Edit)
    1. Create Project (Open, Esc, Open, Fill, Save, Verify)
    2. Edit Project via Table (Open, Cancel)
    3. Edit Project via Inspector (Open, Save, Verify)
    """
    
    # --- SETUP ---
    # Visit Explorer
    page.goto("http://localhost:8000/explorer")
    
    # Handle potentially unauthenticated state (Basic check)
    if "login" in page.url:
        page.fill("input[name='username']", "user@example.com")
        page.fill("input[name='password']", "password")
        page.click("button[type='submit']")
        page.wait_for_url("http://localhost:8000/")
        page.goto("http://localhost:8000/explorer")
        
    # Ensure "Projects" is selected (Default usually, but good to be sure)
    # Assuming the mock data has "Projects"
    
    # --- PART 1: CREATE PROJECT ---
    
    # 1. Open Modal
    page.click("button:has-text('New')")
    
    # 2. Verify Modal Visibility
    modal = page.locator("#modal-container")
    expect(modal).to_be_visible()
    expect(modal).to_contain_text("Create Project")
    
    # 3. Test ESC Key closing
    page.keyboard.press("Escape")
    expect(modal).not_to_be_visible()
    
    # 4. Open again and Create
    page.click("button:has-text('New')")
    expect(modal).to_be_visible()
    
    project_name = "E2E-Auto-Project"
    description = "Created by Playwright Automation"
    
    page.fill("input[name='name']", project_name)
    page.fill("textarea[name='description']", description)
    
    page.click("button[type='submit']")
    
    # 5. Verify Modal Closed & Data in Table
    expect(modal).not_to_be_visible()
    
    # Wait for list refresh (HTMX swap)
    list_container = page.locator("#entity-list-container")
    expect(list_container).to_contain_text(project_name)
    
    # --- PART 2: EDIT VIA TABLE ---
    
    # 1. Find the row with our new project and click the edit button
    # The Edit button is inside the row. We look for a row containing our text.
    row = page.locator(f"tr:has-text('{project_name}')")
    edit_btn_table = row.locator("button[title='Edit']")
    
    # Ensure row exists
    expect(row).to_be_visible()
    
    edit_btn_table.click()
    
    # 2. Verify Edit Modal
    expect(modal).to_be_visible()
    expect(modal).to_contain_text("Edit Project")
    # Check pre-fill
    expect(page.locator("input[name='name']")).to_have_value(project_name)
    
    # 3. Cancel
    page.click("button:has-text('Cancel')")
    expect(modal).not_to_be_visible()
    
    # --- PART 3: EDIT VIA INSPECTOR ---
    
    # 1. Click the row to open Inspector
    row.click()
    
    # 2. Verify Inspector Content
    inspector = page.locator("#explorer-inspector-panel")
    expect(inspector).to_contain_text(project_name)
    expect(inspector).to_contain_text(description)
    
    # 3. Click Edit in Inspector
    edit_btn_inspector = inspector.locator("button[title='Edit']")
    edit_btn_inspector.click()
    
    # 4. Verify Edit Modal
    expect(modal).to_be_visible()
    expect(modal).to_contain_text("Edit Project")
    
    # 5. Update Name
    updated_name = "E2E-Project-Updated"
    page.fill("input[name='name']", updated_name)
    page.click("button[type='submit']")
    
    # 6. Verify Updates (Modal Closed, Inspector Updated, List Updated)
    expect(modal).not_to_be_visible()
    expect(inspector).to_contain_text(updated_name)
    expect(list_container).to_contain_text(updated_name)
    
    # Cleanup (Optional, but good for repeatability if backend doesn't reset)
    # delete_btn = inspector.locator("button[title='Delete']")
    # delete_btn.click()
    # expect(inspector).to_contain_text("Select an item")
