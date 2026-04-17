from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

BASE_URL = "https://www.saucedemo.com"

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        # CI mein 20 second — locally 10 kaafi tha
        self.wait = WebDriverWait(driver, 20)

    def open(self, path="/"):
        self.driver.get(BASE_URL + path)

    def click(self, by, value):
        element = self.wait.until(
            EC.element_to_be_clickable((by, value))
        )
        # CI mein element dikhta hai lekin click nahi hota
        # JavaScript click use karo — zyada reliable
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def type(self, by, value, text):
        element = self.wait.until(
            EC.visibility_of_element_located((by, value))
        )
        element.clear()
        element.send_keys(text)

    def get_text(self, by, value):
        element = self.wait.until(
            EC.visibility_of_element_located((by, value))
        )
        return element.text

    def is_visible(self, by, value):
        try:
            self.wait.until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    def get_title(self):
        return self.driver.title

    def get_current_url(self):
        return self.driver.current_url

    def take_screenshot(self, name):
        return self.driver.get_screenshot_as_png()

    def wait_for_url_change(self, old_url, timeout=20):
        # URL change hone ka wait karo
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.current_url != old_url
        )