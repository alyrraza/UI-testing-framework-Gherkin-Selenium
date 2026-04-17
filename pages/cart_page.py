# cart_page.py
# Cart page elements aur actions

from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class CartPage(BasePage):

    URL = "/cart.html"

    # Elements
    CART_ITEMS    = (By.CLASS_NAME, "cart_item")
    CHECKOUT_BTN  = (By.ID, "checkout")
    CONTINUE_BTN  = (By.ID, "continue-shopping")
    ITEM_NAME     = (By.CLASS_NAME, "inventory_item_name")

    def get_cart_items(self):
        # cart mein saare items ki list
        return self.driver.find_elements(*self.CART_ITEMS)

    def is_item_in_cart(self, item_name: str) -> bool:
        # check karo specific item cart mein hai ya nahi
        items = self.driver.find_elements(*self.ITEM_NAME)
        for item in items:
            if item.text == item_name:
                return True
        return False

    def click_checkout(self):
        # Page load hone ka wait karo pehle
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(self.CHECKOUT_BTN)
        )
        self.click(*self.CHECKOUT_BTN)