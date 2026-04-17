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
        # checkout button visible hone ka wait
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(self.CHECKOUT_BTN)
        )
        # JavaScript se click karo — CI mein zyada reliable
        btn = self.driver.find_element(*self.CHECKOUT_BTN)
        self.driver.execute_script("arguments[0].click();", btn)
        # checkout page load hone ka wait
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "checkout_info_container"))
        )