# pulseq/utilities/driver_manager.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from pulseq.utilities.logger import setup_logger

logger = setup_logger("driver_manager")


def initialize_driver(browser="chrome", headless=True):
    """
    Initializes the WebDriver with specified browser and options.

    Args:
        browser (str): Browser to use ('chrome' or 'firefox')
        headless (bool): Whether to run in headless mode

    Returns:
        WebDriver: Initialized WebDriver instance
    """
    if browser.lower() == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
    elif browser.lower() == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")

        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()), options=options
        )
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    driver.maximize_window()
    logger.info(
        f"Initialized {browser} WebDriver in {'headless' if headless else 'headed'} mode"
    )
    return driver


def quit_driver(driver):
    """Gracefully quits the WebDriver session."""
    if driver:
        driver.quit()
        logger.info("WebDriver session terminated")
