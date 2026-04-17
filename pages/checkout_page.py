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
        from selenium.webdriver.common.keys import Keys

        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, "first-name"))
        )
        time.sleep(0.5)

        for field_id, value in [
            ("first-name", first),
            ("last-name", last),
            ("postal-code", zip_code)
        ]:
            field = self.driver.find_element(By.ID, field_id)
            field.click()
            # Select all aur delete
            field.send_keys(Keys.CONTROL + "a")
            field.send_keys(Keys.DELETE)
            time.sleep(0.1)
            if value:
                field.send_keys(value)
            time.sleep(0.2)

    def click_continue(self):
        self.click(*self.CONTINUE_BTN)

    def click_finish(self):
        self.click(*self.FINISH_BTN)

    def get_complete_message(self) -> str:
        # "Thank you for your order!" padhо
        return self.get_text(*self.COMPLETE_HEADER)

    def get_error_message(self) -> str:
        return self.get_text(*self.ERROR_MESSAGE)