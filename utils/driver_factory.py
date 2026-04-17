import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

def get_driver(browser: str = None, headless: bool = False):
    
    browser = (browser or os.getenv("BROWSER", "chrome")).lower()

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        
        if headless or os.getenv("CI"):
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        
        # Selenium 4.10+ mein built-in driver manager hai
        # Automatically sahi version dhundhta hai
        # webdriver_manager ki zaroorat nahi
        return webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        
        if headless or os.getenv("CI"):
            options.add_argument("--headless")
        
        return webdriver.Firefox(options=options)

    else:
        raise ValueError(
            f"Browser '{browser}' supported nahi"
        )