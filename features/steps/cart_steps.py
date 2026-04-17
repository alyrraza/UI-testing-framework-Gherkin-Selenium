# cart_steps.py

from behave import given, when, then
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage

@given('I am logged in as "{username}"')
def step_login_as(context, username):
    # Login karo pehle
    context.login_page = LoginPage(context.driver)
    context.login_page.open_login()
    context.login_page.login(username, "secret_sauce")
    context.inventory_page = InventoryPage(context.driver)

@when('I add "{product_name}" to the cart')
def step_add_to_cart(context, product_name):
    # Product cart mein daalo
    context.inventory_page.add_to_cart(product_name)

@when('I remove "{product_name}" from the cart')
def step_remove_from_cart(context, product_name):
    context.inventory_page.remove_from_cart(product_name)

@then('the cart count should be "{expected_count}"')
def step_verify_cart_count(context, expected_count):
    # Cart mein kitne items hain check karo
    actual_count = context.inventory_page.get_cart_count()
    assert actual_count == expected_count, \
        f"Expected cart count '{expected_count}', got '{actual_count}'"

@when('I navigate to the cart')
def step_go_to_cart(context):
    context.inventory_page.go_to_cart()
    context.cart_page = CartPage(context.driver)

@then('I should see "{item_name}" in the cart')
def step_verify_item_in_cart(context, item_name):
    # Cart mein specific item hai ya nahi
    assert context.cart_page.is_item_in_cart(item_name), \
        f"'{item_name}' not found in cart"