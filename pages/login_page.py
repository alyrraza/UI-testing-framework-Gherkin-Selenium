# login_page.py
# SauceDemo login page ke saare elements aur actions

from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):

    # Page URL
    URL = "/"

    # Elements — By.ID matlab HTML mein id attribute
    # Jaise: <input id="user-name" />
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON   = (By.ID, "login-button")
    ERROR_MESSAGE  = (By.CSS_SELECTOR, "[data-test='error']")

    def open_login(self):
        # login page kholo
        self.open(self.URL)

    def enter_username(self, username: str):
        # username field mein text likho
        self.type(*self.USERNAME_INPUT, username)

    def enter_password(self, password: str):
        # password field mein text likho
        self.type(*self.PASSWORD_INPUT, password)

    def click_login(self):
        # login button click karo
        self.click(*self.LOGIN_BUTTON)

    def login(self, username: str, password: str):
        # complete login — teen steps ek saath
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def get_error_message(self) -> str:
        # error message ka text padhо
        return self.get_text(*self.ERROR_MESSAGE)

    def is_error_visible(self) -> bool:
        # error message visible hai ya nahi
        return self.is_visible(*self.ERROR_MESSAGE)