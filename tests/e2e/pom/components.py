"""Common UI Components Page Object."""

from playwright.sync_api import Page, Locator, expect
from .base_page import BasePage

class ModalComponent(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.container = page.locator("#modal-container").last
        self.title = self.container.locator("h3") # Assuming title is h3 or similar, adjusting based on test content
        self.submit_button = self.container.locator("button[type='submit']")
        self.cancel_button = self.container.locator("button:has-text('Cancel')")
    
    def is_visible(self) -> bool:
        return self.container.locator("form").is_visible()

    def expect_visible(self) -> None:
        expect(self.container.locator("form")).to_be_visible()

    def expect_hidden(self) -> None:
        expect(self.container).not_to_be_visible()

    def expect_title(self, text: str) -> None:
        expect(self.container).to_contain_text(text)

    def fill_input(self, name: str, value: str) -> None:
        self.container.locator(f"input[name='{name}']").fill(value)

    def fill_textarea(self, name: str, value: str) -> None:
        self.container.locator(f"textarea[name='{name}']").fill(value)

    def submit(self) -> None:
        self.submit_button.click()

    def cancel(self) -> None:
        self.cancel_button.click()

class InspectorPanel(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.panel = page.locator("#inspector-panel #explorer-inspector-panel")
        self.edit_button = self.panel.locator("button[title='Edit']")
        self.delete_button = self.panel.locator("button[title='Delete']")

    def expect_content(self, text: str) -> None:
        expect(self.panel).to_contain_text(text)
    
    def click_edit(self) -> None:
        self.edit_button.click()
    
    def click_delete(self) -> None:
        self.delete_button.click()
