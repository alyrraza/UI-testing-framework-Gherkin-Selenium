# environment.py
# Har test se pehle aur baad mein kya karna hai
# Real world: Restaurant mein
# Before: Table saaf karo, menu rakh do
# After: Table saaf karo, bill do

from utils.driver_factory import get_driver
from utils.allure_utils import attach_screenshot

def before_all(context):
    # Poori test suite shuru hone se pehle
    # context = shared data bag — sab steps isko access kar sakte hain
    context.browser = "chrome"

def before_scenario(context, scenario):
    # Har scenario se pehle — fresh browser kholo
    # Jaise har test case ke liye naya browser window
    context.driver = get_driver(browser=context.browser)
    context.driver.implicitly_wait(10)

def after_scenario(context, scenario):
    # Har scenario ke baad
    if scenario.status == "failed":
        # Test fail hua — screenshot lo evidence ke liye
        attach_screenshot(context.driver, f"FAILED: {scenario.name}")

    # Browser band karo — memory free karo
    if hasattr(context, "driver"):
        context.driver.quit()

def after_all(context):
    # Poori suite khatam — kuch cleanup karo
    pass