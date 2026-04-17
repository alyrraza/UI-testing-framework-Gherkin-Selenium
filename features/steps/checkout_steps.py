from behave import when, then
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage

@when('I click checkout')
def step_click_checkout(context):
    context.cart_page = CartPage(context.driver)
    context.cart_page.click_checkout()
    context.checkout_page = CheckoutPage(context.driver)

@when('I enter first name "{first}" last name "{last}" zip "{zip_code}"')
def step_enter_info(context, first, last, zip_code):
    context.checkout_page.enter_info(first, last, zip_code)

@when(u'I enter first name "" last name "Raza" zip "12345"')
def step_enter_empty_firstname(context):
    context.checkout_page.enter_info("", "Raza", "12345")

@when(u'I enter first name "Ali" last name "Raza" zip ""')
def step_enter_empty_zip(context):
    context.checkout_page.enter_info("Ali", "Raza", "")

@when('I click continue')
def step_click_continue(context):
    context.checkout_page.click_continue()

@then('I should see the order summary')
def step_verify_summary(context):
    current_url = context.driver.current_url
    assert "checkout-step-two" in current_url, \
        f"Expected order summary, got: {current_url}"

@when('I click finish')
def step_click_finish(context):
    context.checkout_page.click_finish()

@then('I should see "{expected_message}"')
def step_verify_complete(context, expected_message):
    actual = context.checkout_page.get_complete_message()
    assert expected_message in actual, \
        f"Expected '{expected_message}', got '{actual}'"

@then('I should see an error "{expected_error}"')
def step_verify_checkout_error(context, expected_error):
    actual = context.checkout_page.get_error_message()
    assert expected_error in actual, \
        f"Expected '{expected_error}', got '{actual}'"