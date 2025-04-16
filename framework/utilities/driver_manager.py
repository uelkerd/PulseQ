# framework/utilities/driver_manager.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def initialize_driver(headless=True):
    """Initializes the Chrome WebDriver with optional headless mode."""
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Additional options can be added here
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    driver.maximize_window()
    return driver


def quit_driver(driver):
    """Gracefully quits the WebDriver session."""
    if driver:
        driver.quit()
