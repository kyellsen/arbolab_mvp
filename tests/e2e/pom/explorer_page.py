"""Explorer Page Object."""

from playwright.sync_api import Page, expect
from .base_page import BasePage
from .components import ModalComponent, InspectorPanel

class ExplorerPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page)
        self.base_url = base_url
        self.new_button = page.locator("#main-stage button", has_text="New").first
        self.list_container = page.locator("#entity-list-container")
        self.modal = ModalComponent(page)
        self.inspector = InspectorPanel(page)

    def navigate_to(self) -> None:
        self.navigate(self.base_url)
        self.page.locator("a[data-nav-path='/explorer']").click()
        expect(self.list_container).to_be_visible()
        
    def click_new(self) -> None:
        self.new_button.click()

    def select_category(self, name: str) -> None:
        self.page.get_by_role("button", name=name).click()

    def get_row(self, text: str):
        return self.page.locator(f"tr:has-text('{text}')")

    def click_row_edit(self, row_text: str) -> None:
        row = self.get_row(row_text)
        row.locator("button[title='Edit']").click()
    
    def select_row(self, row_text: str) -> None:
        self.get_row(row_text).click()

    def expect_in_list(self, text: str) -> None:
        expect(self.list_container).to_contain_text(text)
    
    def expect_not_in_list(self, text: str) -> None:
        expect(self.list_container).not_to_contain_text(text)
