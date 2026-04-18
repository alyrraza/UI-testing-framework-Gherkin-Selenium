"""
InventoryPage — Products listing after login.

Migrated by Claude Opus 4.7 to use SmartLocator for every static element.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.smart_locator import SmartLocator


class InventoryPage(BasePage):

    URL = "/inventory.html"

    PAGE_TITLE = SmartLocator(
        name="inventory_page_title",
        description="Header title on the products page (shows 'Products')",
        expected_tag="span",
        expected_text="products",
        strategies=[
            (By.CLASS_NAME, "title"),
            (By.CSS_SELECTOR, ".header_secondary_container .title"),
            (By.XPATH, "//*[contains(@class,'title')]"),
        ],
    )

    CART_BADGE = SmartLocator(
        name="cart_count_badge",
        description="Small badge on the cart icon showing item count",
        strategies=[
            (By.CLASS_NAME, "shopping_cart_badge"),
            (By.CSS_SELECTOR, ".shopping_cart_link .shopping_cart_badge"),
        ],
    )

    CART_ICON = SmartLocator(
        name="cart_icon_link",
        description="Shopping cart icon in the top right header",
        strategies=[
            (By.CLASS_NAME, "shopping_cart_link"),
            (By.CSS_SELECTOR, "a[href*='cart']"),
        ],
    )

    BURGER_MENU = SmartLocator(
        name="burger_menu_button",
        description="Hamburger menu button that opens the side drawer",
        expected_tag="button",
        strategies=[
            (By.ID, "react-burger-menu-btn"),
            (By.CSS_SELECTOR, "button.bm-burger-button"),
            (By.XPATH, "//button[contains(@class,'burger')]"),
        ],
    )

    LOGOUT_LINK = SmartLocator(
        name="logout_sidebar_link",
        description="Logout link inside the side drawer menu",
        expected_text="logout",
        strategies=[
            (By.ID, "logout_sidebar_link"),
            (By.XPATH, "//a[normalize-space(text())='Logout']"),
            (By.CSS_SELECTOR, "a[data-test='logout-sidebar-link']"),
        ],
    )

    # ----------------------------------------------------------------- reads

    def get_page_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def get_cart_count(self) -> str:
        if self.is_visible(self.CART_BADGE):
            return self.get_text(self.CART_BADGE)
        return "0"

    # ---------------------------------------------------------------- writes

    def add_to_cart(self, product_name: str):
        """Find the product's Add-to-cart button by walking up from the title."""
        button_xpath = (
            By.XPATH,
            f"//div[text()='{product_name}']"
            f"/ancestor::div[@class='inventory_item']"
            f"//button",
        )
        btn = self.driver.find_element(*button_xpath)
        self.driver.execute_script("arguments[0].click();", btn)
        self.smart_wait.wait_for_dom_stable(timeout=5, quiet_ms=300)

    def remove_from_cart(self, product_name: str):
        button_xpath = (
            By.XPATH,
            f"//div[text()='{product_name}']"
            f"/ancestor::div[@class='inventory_item']"
            f"//button[text()='Remove']",
        )
        btn = self.driver.find_element(*button_xpath)
        self.driver.execute_script("arguments[0].click();", btn)

        # Wait for the toggle back to "Add to cart" — deterministic end-state.
        add_btn_xpath = (
            By.XPATH,
            f"//div[text()='{product_name}']"
            f"/ancestor::div[@class='inventory_item']"
            f"//button[text()='Add to cart']",
        )
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located(add_btn_xpath)
        )

    def go_to_cart(self):
        self.driver.get("https://www.saucedemo.com/cart.html")

    def open_burger_menu(self):
        self.click(self.BURGER_MENU)

    def click_logout(self):
        self.click(self.LOGOUT_LINK)

    def logout(self):
        self.open_burger_menu()
        self.smart_wait.wait_for_dom_stable(timeout=5, quiet_ms=300)
        self.click_logout()
