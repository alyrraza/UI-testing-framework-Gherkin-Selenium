from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

class CartPage(BasePage):

    URL = "/cart.html"
    CART_ITEMS   = (By.CLASS_NAME, "cart_item")
    CHECKOUT_BTN = (By.ID, "checkout")
    CONTINUE_BTN = (By.ID, "continue-shopping")
    ITEM_NAME    = (By.CLASS_NAME, "inventory_item_name")

    def get_cart_items(self):
        return self.driver.find_elements(*self.CART_ITEMS)

    def is_item_in_cart(self, item_name: str) -> bool:
        items = self.driver.find_elements(*self.ITEM_NAME)
        for item in items:
            if item.text == item_name:
                return True
        return False

    def click_checkout(self):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time
        time.sleep(1)
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(self.CHECKOUT_BTN)
        )
        btn = self.driver.find_element(*self.CHECKOUT_BTN)
        self.driver.execute_script("arguments[0].click();", btn)
        WebDriverWait(self.driver, 20).until(
            EC.url_contains("checkout-step-one")
        )