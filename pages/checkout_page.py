# checkout_page.py
# Checkout pages elements aur actions

from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class CheckoutPage(BasePage):

    # Elements — Step 1
    FIRST_NAME_INPUT = (By.ID, "first-name")
    LAST_NAME_INPUT  = (By.ID, "last-name")
    ZIP_INPUT        = (By.ID, "postal-code")
    CONTINUE_BTN     = (By.ID, "continue")
    ERROR_MESSAGE    = (By.CSS_SELECTOR, "[data-test='error']")

    # Elements — Step 2 (Order Summary)
    FINISH_BTN       = (By.ID, "finish")
    SUMMARY_INFO     = (By.CLASS_NAME, "summary_info")

    # Elements — Complete
    COMPLETE_HEADER  = (By.CLASS_NAME, "complete-header")

    def enter_info(self, first: str, last: str, zip_code: str):
        import time
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, "first-name"))
        )
        time.sleep(1)

        # React fields ke liye yeh single reliable method hai
        def set_react_field(field_id, value):
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
            time.sleep(0.3)

        set_react_field("first-name", first)
        set_react_field("last-name", last)
        set_react_field("postal-code", zip_code)
        time.sleep(0.5)

    def click_continue(self):
        self.click(*self.CONTINUE_BTN)

    def click_finish(self):
        self.click(*self.FINISH_BTN)

    def get_complete_message(self) -> str:
        # "Thank you for your order!" padhо
        return self.get_text(*self.COMPLETE_HEADER)

    def get_error_message(self) -> str:
        return self.get_text(*self.ERROR_MESSAGE)