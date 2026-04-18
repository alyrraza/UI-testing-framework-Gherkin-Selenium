"""
LoginPage — SauceDemo login screen.

Migrated by Claude Opus 4.7 to use SmartLocator. Every element now carries
a prioritized list of fallback strategies. If the primary ID selector breaks
(e.g. SauceDemo ships an A/B test that renames `login-button` to `sign-in`),
the framework heals automatically via the fallback chain or DOM similarity.
"""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.smart_locator import SmartLocator


class LoginPage(BasePage):

    URL = "/"

    USERNAME_INPUT = SmartLocator(
        name="login_username",
        description="Username input on the login form",
        expected_tag="input",
        strategies=[
            (By.ID, "user-name"),
            (By.CSS_SELECTOR, "[data-test='username']"),
            (By.NAME, "user-name"),
            (By.CSS_SELECTOR, "input[placeholder*='Username']"),
        ],
    )

    PASSWORD_INPUT = SmartLocator(
        name="login_password",
        description="Password input on the login form",
        expected_tag="input",
        strategies=[
            (By.ID, "password"),
            (By.CSS_SELECTOR, "[data-test='password']"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
        ],
    )

    LOGIN_BUTTON = SmartLocator(
        name="login_submit_button",
        description="Submit button on the login form",
        expected_tag="input",
        expected_text="login",
        strategies=[
            (By.ID, "button-renamed-by-dev"),  #to crash it
            (By.CSS_SELECTOR, "[data-test='login-button']"),
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.XPATH, "//input[@value='Login']"),
        ],
    )

    ERROR_MESSAGE = SmartLocator(
        name="login_error_message",
        description="Inline error banner shown after a failed login",
        strategies=[
            (By.CSS_SELECTOR, "[data-test='error']"),
            (By.CSS_SELECTOR, ".error-message-container h3"),
            (By.XPATH, "//*[contains(@class,'error')]//h3"),
        ],
    )

    # ---------------------------------------------------------------- actions

    def open_login(self):
        self.open(self.URL)

    def enter_username(self, username: str):
        self.type(self.USERNAME_INPUT, username)

    def enter_password(self, password: str):
        self.type(self.PASSWORD_INPUT, password)

    def click_login(self):
        self.click(self.LOGIN_BUTTON)

    def login(self, username: str, password: str):
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_visible(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE)
