from behave import when, then
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

@when('I click checkout')
def step_click_checkout(context):
    context.cart_page = CartPage(context.driver)
    context.cart_page.click_checkout()
    context.checkout_page = CheckoutPage(context.driver)
    # Step one load hone ka wait
    WebDriverWait(context.driver, 20).until(
        EC.presence_of_element_located((By.ID, "first-name"))
    )

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
    import time
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    time.sleep(1)
    btn = WebDriverWait(context.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "continue"))
    )
    context.driver.execute_script("arguments[0].click();", btn)
    time.sleep(3)

@then('I should see the order summary')
def step_verify_summary(context):
    current_url = context.driver.current_url
    if "checkout-step-two" not in current_url:
        # Ek aur try
        try:
            context.driver.execute_script("""
                document.querySelector('form').submit();
            """)
            time.sleep(3)
        except:
            pass
    current_url = context.driver.current_url
    assert "checkout-step-two" in current_url, \
        f"Expected order summary, got: {current_url}"

@when('I click finish')
def step_click_finish(context):
    WebDriverWait(context.driver, 20).until(
        EC.element_to_be_clickable((By.ID, "finish"))
    )
    btn = context.driver.find_element(By.ID, "finish")
    context.driver.execute_script("arguments[0].click();", btn)

@then('I should see "{expected_message}"')
def step_verify_complete(context, expected_message):
    WebDriverWait(context.driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "complete-header"))
    )
    actual = context.checkout_page.get_complete_message()
    assert expected_message in actual, \
        f"Expected '{expected_message}', got '{actual}'"

@then('I should see an error "{expected_error}"')
def step_verify_checkout_error(context, expected_error):
    # Error dikhne ka wait — 15 second
    time.sleep(2)
    try:
        WebDriverWait(context.driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-test='error']")
            )
        )
        actual = context.checkout_page.get_error_message()
    except:
        # Error element nahi mila — current page check karo
        actual = context.driver.find_element(
            By.CSS_SELECTOR, "[data-test='error']"
        ).text if context.driver.find_elements(
            By.CSS_SELECTOR, "[data-test='error']"
        ) else "No error found"

    assert expected_error in actual, \
        f"Expected '{expected_error}', got '{actual}'"