"""
CartPage — SauceDemo cart.

Migrated by Claude Opus 4.7 to use SmartLocator.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.smart_locator import SmartLocator


class CartPage(BasePage):

    URL = "/cart.html"

    CART_ITEMS = SmartLocator(
        name="cart_item_rows",
        description="Rows in the cart listing",
        strategies=[
            (By.CLASS_NAME, "cart_item"),
            (By.CSS_SELECTOR, ".cart_list .cart_item"),
        ],
    )

    CHECKOUT_BTN = SmartLocator(
        name="cart_checkout_button",
        description="Checkout button at the cart footer",
        expected_tag="button",
        expected_text="checkout",
        strategies=[
            (By.ID, "checkout"),
            (By.CSS_SELECTOR, "[data-test='checkout']"),
            (By.XPATH, "//button[normalize-space(text())='Checkout']"),
        ],
    )

    CONTINUE_BTN = SmartLocator(
        name="cart_continue_shopping_button",
        description="Continue-shopping button on the cart page",
        expected_tag="button",
        strategies=[
            (By.ID, "continue-shopping"),
            (By.CSS_SELECTOR, "[data-test='continue-shopping']"),
        ],
    )

    ITEM_NAME = SmartLocator(
        name="cart_item_name_label",
        description="Product name label inside a cart row",
        strategies=[
            (By.CLASS_NAME, "inventory_item_name"),
            (By.CSS_SELECTOR, ".cart_item .inventory_item_name"),
        ],
    )

    # ---------------------------------------------------------------- reads

    def get_cart_items(self):
        return self.driver.find_elements(*self.CART_ITEMS.as_tuple())

    def is_item_in_cart(self, item_name: str) -> bool:
        items = self.driver.find_elements(*self.ITEM_NAME.as_tuple())
        return any(item.text == item_name for item in items)

    # ---------------------------------------------------------------- actions

    def click_checkout(self):
        self.smart_wait.wait_for_dom_stable(timeout=5, quiet_ms=300)
        btn = self.CHECKOUT_BTN.find_clickable(self.driver, timeout=20)
        self.driver.execute_script("arguments[0].click();", btn)
        WebDriverWait(self.driver, 20).until(EC.url_contains("checkout-step-one"))
