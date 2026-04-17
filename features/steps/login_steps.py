# login_steps.py
# Gherkin steps ko actual Python code se connect karta hai
# Real world: Director ka script → Actor ka actual performance

from behave import given, when, then
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

@given('I am on the SauceDemo login page')
def step_open_login(context):
    # Login page kholo
    # context.driver = browser jo environment.py ne banaya
    context.login_page = LoginPage(context.driver)
    context.login_page.open_login()

@when('I enter username "{username}" and password "{password}"')
def step_enter_credentials(context, username, password):
    # normal case — value ke saath
    context.login_page.enter_username(username)
    context.login_page.enter_password(password)
@when(u'I enter username "" and password ""')
def step_enter_empty_credentials(context):
    # empty credentials case
    # khali string pass karo
    context.login_page.enter_username("")
    context.login_page.enter_password("")

@when('I click the login button')
def step_click_login(context):
    context.login_page.click_login()

@then('I should be on the inventory page')
def step_verify_inventory(context):
    # Check karo URL mein "inventory" hai
    current_url = context.driver.current_url
    assert "inventory" in current_url, \
        f"Expected inventory page, got: {current_url}"

@then('the page title should be "{expected_title}"')
def step_verify_title(context, expected_title):
    # Products page ka title check karo
    context.inventory_page = InventoryPage(context.driver)
    actual_title = context.inventory_page.get_page_title()
    assert actual_title == expected_title, \
        f"Expected '{expected_title}', got '{actual_title}'"

@then('I should see an error message containing "{expected_error}"')
def step_verify_error(context, expected_error):
    # Error message check karo
    actual_error = context.login_page.get_error_message()
    assert expected_error in actual_error, \
        f"Expected '{expected_error}' in '{actual_error}'"

@when('I open the burger menu and click logout')
def step_logout(context, ):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    import time

    context.inventory_page = InventoryPage(context.driver)

    # burger menu click karo
    context.inventory_page.open_burger_menu()

    # sidebar open hone ka explicit wait
    WebDriverWait(context.driver, 15).until(
        EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))
    )
    time.sleep(0.5)

    # logout click karo JavaScript se
    logout_btn = context.driver.find_element(By.ID, "logout_sidebar_link")
    context.driver.execute_script("arguments[0].click();", logout_btn)


@then('I should be on the login page')
def step_verify_login_page(context):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    # login page load hone ka wait
    WebDriverWait(context.driver, 20).until(
        EC.presence_of_element_located((By.ID, "login-button"))
    )
    current_url = context.driver.current_url
    assert "inventory" not in current_url, \
        f"Still on inventory page: {current_url}"

@then('the login result should be "{expected_result}"')
def step_verify_login_result(context, expected_result):
    # Data driven test — success ya failure check karo
    current_url = context.driver.current_url
    if expected_result == "success":
        assert "inventory" in current_url, \
            f"Expected success but got: {current_url}"
    else:
        assert context.login_page.is_error_visible(), \
            "Expected error message but none shown"