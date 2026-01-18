"""Base Page Object."""

from playwright.sync_api import Page, expect

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str) -> None:
        self.page.goto(url)

    def wait_for_url(self, url: str) -> None:
        self.page.wait_for_url(url)
