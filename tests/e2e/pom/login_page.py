"""Login Page Object."""

from playwright.sync_api import Page
from .base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page: Page, base_url: str):
        super().__init__(page)
        self.base_url = base_url
        self.username_input = page.locator("input[name='username']")
        self.password_input = page.locator("input[name='password']")
        self.submit_button = page.locator("button[type='submit']")

    def login(self, username: str = "mail@kyell.de", password: str = "123") -> None:
        self.navigate(f"{self.base_url}/auth/login")
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.submit_button.click()
        self.wait_for_url(f"{self.base_url}/")
