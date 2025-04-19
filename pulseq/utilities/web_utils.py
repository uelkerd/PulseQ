from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pulseq.utilities.logger import setup_logger

logger = setup_logger("web_utils")


class WebUtils:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_for_element(self, locator, timeout=10):
        """Wait for an element to be present and visible."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            logger.error(f"Element not found: {locator}")
            raise

    def wait_for_element_clickable(self, locator, timeout=10):
        """Wait for an element to be clickable."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            logger.error(f"Element not clickable: {locator}")
            raise

    def is_element_present(self, locator):
        """Check if an element is present on the page."""
        try:
            self.driver.find_element(*locator)
            return True
        except:
            return False
