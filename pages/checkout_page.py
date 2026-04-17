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
            EC.presence_of_element_located((By.ID, "first-name"))
        )
        time.sleep(1)

        # JavaScript se directly value set karo — send_keys se pehle
        self.driver.execute_script(
            "document.getElementById('first-name').value = arguments[0];",
            first
        )
        self.driver.execute_script(
            "document.getElementById('last-name').value = arguments[0];",
            last
        )
        self.driver.execute_script(
            "document.getElementById('postal-code').value = arguments[0];",
            zip_code
        )

        # React ke liye events trigger karo
        for field_id in ["first-name", "last-name", "postal-code"]:
            self.driver.execute_script(f"""
                var el = document.getElementById('{field_id}');
                var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(el, el.value);
                el.dispatchEvent(new Event('input', {{bubbles: true}}));
                el.dispatchEvent(new Event('change', {{bubbles: true}}));
            """)
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