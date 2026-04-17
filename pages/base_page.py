# base_page.py
# Yeh sab pages ki "maa" class hai
# Common functions yahan hain jo har page use karta hai

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

BASE_URL = "https://www.saucedemo.com"

class BasePage:
    # constructor — har page object ko driver chahiye
    def __init__(self, driver):
        self.driver = driver
        # WebDriverWait — element ke aane ka wait karo
        # 10 seconds tak wait karega, phir error
        self.wait = WebDriverWait(driver, 10)

    def open(self, path="/"):
        # URL kholo
        # path = "/login" toh URL = "https://www.saucedemo.com/login"
        self.driver.get(BASE_URL + path)

    def click(self, by, value):
        # element dhundho aur click karo
        # pehle wait karo ke element visible ho
        element = self.wait.until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()

    def type(self, by, value, text):
        # input field mein text likho
        # pehle field clear karo, phir likho
        element = self.wait.until(
            EC.visibility_of_element_located((by, value))
        )
        element.clear()
        element.send_keys(text)

    def get_text(self, by, value):
        # element ka text padhо
        element = self.wait.until(
            EC.visibility_of_element_located((by, value))
        )
        return element.text

    def is_visible(self, by, value):
        # check karo element visible hai ya nahi
        try:
            self.wait.until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            # 10 second mein nahi mila — False return karo
            return False

    def get_title(self):
        # page ka title padhо
        return self.driver.title

    def get_current_url(self):
        # current URL padhо
        return self.driver.current_url

    def take_screenshot(self, name):
        # screenshot lo — Allure report ke liye
        return self.driver.get_screenshot_as_png()