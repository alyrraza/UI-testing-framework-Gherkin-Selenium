# inventory_page.py
# Products page — login ke baad yahan aate hain

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

class InventoryPage(BasePage):

    URL = "/inventory.html"

    # Elements
    PAGE_TITLE      = (By.CLASS_NAME, "title")
    CART_BADGE      = (By.CLASS_NAME, "shopping_cart_badge")
    CART_ICON       = (By.CLASS_NAME, "shopping_cart_link")
    BURGER_MENU     = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK     = (By.ID, "logout_sidebar_link")
    INVENTORY_ITEMS = (By.CLASS_NAME, "inventory_item")

    def get_page_title(self) -> str:
        # page title padhо — "Products" hona chahiye
        return self.get_text(*self.PAGE_TITLE)

    def get_cart_count(self) -> str:
        # cart mein kitne items hain
        if self.is_visible(*self.CART_BADGE):
            return self.get_text(*self.CART_BADGE)
        # badge nahi dikhta matlab cart khali hai
        return "0"

    def add_to_cart(self, product_name: str):
        # product name se Add to Cart button dhundho aur click karo
        # XPath use kar rahe hain — complex selector
        # Matlab: "Sauce Labs Backpack" wale item ka button dhundho
        button_xpath = (
            By.XPATH,
            f"//div[text()='{product_name}']"
            f"/ancestor::div[@class='inventory_item']"
            f"//button"
        )
        self.click(*button_xpath)

    def remove_from_cart(self, product_name: str):
        # same logic — Remove button dhundho
        button_xpath = (
            By.XPATH,
            f"//div[text()='{product_name}']"
            f"/ancestor::div[@class='inventory_item']"
            f"//button[text()='Remove']"
        )
        self.click(*button_xpath)

    def go_to_cart(self):
        # cart icon click karo
        self.click(*self.CART_ICON)

    def open_burger_menu(self):
        # hamburger menu kholo
        self.click(*self.BURGER_MENU)

    def click_logout(self):
        # logout link click karo
        self.click(*self.LOGOUT_LINK)

    def logout(self):
        # complete logout
        self.open_burger_menu()
        self.click_logout()