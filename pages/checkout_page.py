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

        # Fields load hone ka wait
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(self.FIRST_NAME_INPUT)
        )
        time.sleep(0.5)

        # Har field properly clear karke fill karo
        first_field = self.driver.find_element(*self.FIRST_NAME_INPUT)
        self.driver.execute_script("arguments[0].value = '';", first_field)
        first_field.send_keys(first)

        last_field = self.driver.find_element(*self.LAST_NAME_INPUT)
        self.driver.execute_script("arguments[0].value = '';", last_field)
        last_field.send_keys(last)

        zip_field = self.driver.find_element(*self.ZIP_INPUT)
        self.driver.execute_script("arguments[0].value = '';", zip_field)
        zip_field.send_keys(zip_code)

    def click_continue(self):
        self.click(*self.CONTINUE_BTN)

    def click_finish(self):
        self.click(*self.FINISH_BTN)

    def get_complete_message(self) -> str:
        # "Thank you for your order!" padhо
        return self.get_text(*self.COMPLETE_HEADER)

    def get_error_message(self) -> str:
        return self.get_text(*self.ERROR_MESSAGE)