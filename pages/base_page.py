"""
BasePage — foundation for all page objects.

Extended by Claude Opus 4.7 to support self-healing locators and intelligent
page-readiness detection. Every public method now accepts either a classic
Selenium (By, value) tuple *or* a SmartLocator instance — so migrating page
objects is incremental and backwards-compatible.
"""

from typing import Union

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from utils.smart_locator import SmartLocator
from utils.smart_wait import SmartWait


BASE_URL = "https://www.saucedemo.com"

Locator = Union[SmartLocator, tuple]


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.smart_wait = SmartWait(driver)

    # --------------------------------------------------------- navigation

    def open(self, path: str = "/") -> None:
        self.driver.get(BASE_URL + path)
        self.smart_wait.wait_for_page_ready()

    # ------------------------------------------------------- core actions

    def _find(self, locator: Locator, timeout: int = 20) -> WebElement:
        """Unified finder — accepts SmartLocator or (By, value) tuple."""
        if isinstance(locator, SmartLocator):
            return locator.find(self.driver, timeout=timeout)
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def _find_clickable(self, locator: Locator, timeout: int = 20) -> WebElement:
        if isinstance(locator, SmartLocator):
            return locator.find_clickable(self.driver, timeout=timeout)
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def click(self, locator: Locator, *maybe_value) -> None:
        """Click with automatic JS-fallback if the native click fails.

        Accepts three calling conventions for backwards compatibility:
            click(smart_locator)
            click((By.ID, 'foo'))
            click(By.ID, 'foo')       # legacy positional
        """
        locator = self._normalize(locator, maybe_value)
        element = self._find_clickable(locator)
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def type(self, locator: Locator, *args) -> None:
        """Fill a text field. Legacy signature `type(by, value, text)` works too."""
        if len(args) == 2:
            # legacy: type(by, value, text)
            locator = (locator, args[0])
            text = args[1]
        elif len(args) == 1:
            text = args[0]
        else:
            raise TypeError("type() expects a value to type")
        element = self._find(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: Locator, *maybe_value) -> str:
        locator = self._normalize(locator, maybe_value)
        return self._find(locator).text

    def is_visible(self, locator: Locator, *maybe_value) -> bool:
        locator = self._normalize(locator, maybe_value)
        try:
            if isinstance(locator, SmartLocator):
                locator.find(self.driver, timeout=5)
                return True
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
        except Exception:
            return False

    def get_title(self) -> str:
        return self.driver.title

    def get_current_url(self) -> str:
        return self.driver.current_url

    def take_screenshot(self, name: str) -> bytes:
        return self.driver.get_screenshot_as_png()

    def wait_for_url_change(self, old_url: str, timeout: int = 20) -> None:
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.current_url != old_url
        )

    # -------------------------------------------------------------- helpers

    @staticmethod
    def _normalize(locator, maybe_value):
        """Accept (locator,) or legacy (by, value)."""
        if maybe_value:
            return (locator, maybe_value[0])
        return locator
