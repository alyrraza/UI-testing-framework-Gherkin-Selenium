"""
CheckoutPage — SauceDemo checkout flow.

Migrated by Claude Opus 4.7 to use SmartLocator. The React-controlled form
fields still require a native-setter dispatch (otherwise React's virtual DOM
overwrites the value on next render), so that behavior is preserved.
"""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.smart_locator import SmartLocator


class CheckoutPage(BasePage):

    # ---------------------------------------------------------------- step 1
    FIRST_NAME_INPUT = SmartLocator(
        name="checkout_first_name_input",
        description="First name field on checkout step one",
        expected_tag="input",
        strategies=[
            (By.ID, "first-name"),
            (By.CSS_SELECTOR, "[data-test='firstName']"),
            (By.NAME, "firstName"),
        ],
    )

    LAST_NAME_INPUT = SmartLocator(
        name="checkout_last_name_input",
        description="Last name field on checkout step one",
        expected_tag="input",
        strategies=[
            (By.ID, "last-name"),
            (By.CSS_SELECTOR, "[data-test='lastName']"),
            (By.NAME, "lastName"),
        ],
    )

    ZIP_INPUT = SmartLocator(
        name="checkout_postal_code_input",
        description="Zip / postal code field on checkout step one",
        expected_tag="input",
        strategies=[
            (By.ID, "postal-code"),
            (By.CSS_SELECTOR, "[data-test='postalCode']"),
            (By.NAME, "postalCode"),
        ],
    )

    CONTINUE_BTN = SmartLocator(
        name="checkout_continue_button",
        description="Continue button advancing from step one to summary",
        strategies=[
            (By.ID, "continue"),
            (By.CSS_SELECTOR, "[data-test='continue']"),
            (By.CSS_SELECTOR, "input[type='submit']"),
        ],
    )

    ERROR_MESSAGE = SmartLocator(
        name="checkout_error_message",
        description="Inline validation error on checkout step one",
        strategies=[
            (By.CSS_SELECTOR, "[data-test='error']"),
            (By.CSS_SELECTOR, ".error-message-container h3"),
        ],
    )

    # ------------------------------------------------------ step 2 + complete
    FINISH_BTN = SmartLocator(
        name="checkout_finish_button",
        description="Finish button on the order summary page",
        strategies=[
            (By.ID, "finish"),
            (By.CSS_SELECTOR, "[data-test='finish']"),
        ],
    )

    SUMMARY_INFO = SmartLocator(
        name="checkout_summary_info",
        description="Summary panel on the order review step",
        strategies=[(By.CLASS_NAME, "summary_info")],
    )

    COMPLETE_HEADER = SmartLocator(
        name="checkout_complete_header",
        description="Thank-you header on the order complete page",
        strategies=[
            (By.CLASS_NAME, "complete-header"),
            (By.XPATH, "//*[contains(text(),'Thank you')]"),
        ],
    )

    # ----------------------------------------------------------------- actions

    def enter_info(self, first: str, last: str, zip_code: str):
        """React-safe form population using the native setter."""
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, "first-name"))
        )
        time.sleep(0.5)

        def set_react_field(field_id: str, value: str) -> None:
            script = """
            var input = document.getElementById(arguments[0]);
            var nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value').set;
            nativeSetter.call(input, arguments[1]);
            input.dispatchEvent(new Event('input', {bubbles: true}));
            input.dispatchEvent(new Event('change', {bubbles: true}));
            input.dispatchEvent(new Event('blur', {bubbles: true}));
            """
            self.driver.execute_script(script, field_id, value)

        set_react_field("first-name", first)
        set_react_field("last-name", last)
        set_react_field("postal-code", zip_code)
        self.smart_wait.wait_for_dom_stable(timeout=3, quiet_ms=250)

    def click_continue(self):
        self.click(self.CONTINUE_BTN)

    def click_finish(self):
        self.click(self.FINISH_BTN)

    def get_complete_message(self) -> str:
        return self.get_text(self.COMPLETE_HEADER)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)
