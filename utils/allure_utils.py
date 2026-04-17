# allure_utils.py
# Allure report ke liye helper functions
# Real world: Factory ka quality report system

import allure

def attach_screenshot(driver, name="screenshot"):
    # Screenshot lo aur Allure report mein attach karo
    # Jaise factory mein defective product ki photo lo
    screenshot = driver.get_screenshot_as_png()
    allure.attach(
        screenshot,
        name=name,
        attachment_type=allure.attachment_type.PNG
    )

def attach_text(text: str, name="info"):
    # Text information Allure mein attach karo
    allure.attach(
        text,
        name=name,
        attachment_type=allure.attachment_type.TEXT
    )