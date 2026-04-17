from behave import given, when, then
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@given('I am logged in as "{username}"')
def step_login_as(context, username):
    context.login_page = LoginPage(context.driver)
    context.login_page.open_login()
    context.login_page.login(username, "secret_sauce")
    # inventory page load hone ka wait
    WebDriverWait(context.driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "inventory_list"))
    )
    context.inventory_page = InventoryPage(context.driver)

@when('I add "{product_name}" to the cart')
def step_add_to_cart(context, product_name):
    context.inventory_page.add_to_cart(product_name)
    # cart update hone ka wait karo
    time.sleep(1)

@when('I remove "{product_name}" from the cart')
def step_remove_from_cart(context, product_name):
    import time
    from selenium.webdriver.common.by import By

    context.inventory_page.remove_from_cart(product_name)

    # Simple polling — badge disappear hone ka wait
    for _ in range(10):
        badges = context.driver.find_elements(
            By.CLASS_NAME, "shopping_cart_badge"
        )
        if len(badges) == 0:
            return  # badge gone — pass
        time.sleep(0.5)

@then('the cart count should be "{expected_count}"')
def step_verify_cart_count(context, expected_count):
    import time
    from selenium.webdriver.common.by import By

    # 5 second tak check karo
    actual_count = "0"
    for _ in range(10):
        badges = context.driver.find_elements(
            By.CLASS_NAME, "shopping_cart_badge"
        )
        if badges:
            actual_count = badges[0].text
        else:
            actual_count = "0"

        if actual_count == expected_count:
            return  # Pass!
        time.sleep(0.5)

    assert actual_count == expected_count, \
        f"Expected cart count '{expected_count}', got '{actual_count}'"
        
        
@when('I navigate to the cart')
def step_go_to_cart(context):
    # Direct URL pe jao
    context.driver.get("https://www.saucedemo.com/cart.html")
    # Cart items load hone ka wait
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    WebDriverWait(context.driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "cart_item"))
    )
    context.cart_page = CartPage(context.driver)

@then('I should see "{item_name}" in the cart')
def step_verify_item_in_cart(context, item_name):
    assert context.cart_page.is_item_in_cart(item_name), \
        f"'{item_name}' not found in cart"