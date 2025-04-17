# pulseq/utilities/wait_utils.py

import time
from typing import Any, Callable, List, Optional, Tuple, Union

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pulseq.utilities.logger import setup_logger
from pulseq.utilities.misc_utils import MiscUtils

# Set up module logger
logger = setup_logger("wait_utils")


class WaitUtils:
    """
    Provides utility methods for waiting on element conditions.
    Implements both explicit and fluent waiting patterns.
    """

    def __init__(self, driver, timeout=10):
        """
        Initialize the wait utility with a WebDriver instance.

        Args:
            driver: Selenium WebDriver instance
            timeout: Default timeout in seconds
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(
            driver,
            timeout,
            poll_frequency=0.5,
            ignored_exceptions=[StaleElementReferenceException],
        )

    def wait_for_element_visible(self, locator, timeout=None, message=None):
        """
        Wait for an element to be visible on the page.

        Args:
            locator: Element locator tuple (By.XX, "value")
            timeout: Custom timeout in seconds (overrides default)
            message: Custom error message for TimeoutException

        Returns:
            WebElement: The element once visible

        Raises:
            TimeoutException: If element doesn't become visible within timeout
        """
        wait_timeout = timeout if timeout is not None else self.timeout
        error_message = (
            message
            if message
            else f"Element {locator} not visible after {wait_timeout} seconds"
        )

        try:
            logger.debug(f"Waiting for element {locator} to be visible")
            element = WebDriverWait(self.driver, wait_timeout).until(
                EC.visibility_of_element_located(locator)
            )
            logger.debug(f"Element {locator} is now visible")
            return element
        except TimeoutException:
            logger.error(error_message)
            raise TimeoutException(error_message)

    def wait_for_element_clickable(self, locator, timeout=None, message=None):
        """
        Wait for an element to be clickable.

        Args:
            locator: Element locator tuple (By.XX, "value")
            timeout: Custom timeout in seconds (overrides default)
            message: Custom error message for TimeoutException

        Returns:
            WebElement: The element once clickable

        Raises:
            TimeoutException: If element doesn't become clickable within timeout
        """
        wait_timeout = timeout if timeout is not None else self.timeout
        error_message = (
            message
            if message
            else f"Element {locator} not clickable after {wait_timeout} seconds"
        )

        try:
            logger.debug(f"Waiting for element {locator} to be clickable")
            element = WebDriverWait(self.driver, wait_timeout).until(
                EC.element_to_be_clickable(locator)
            )
            logger.debug(f"Element {locator} is now clickable")
            return element
        except TimeoutException:
            logger.error(error_message)
            raise TimeoutException(error_message)

    def wait_for_text_present(self, locator, text, timeout=None, message=None):
        """
        Wait for text to be present in the element.

        Args:
            locator: Element locator tuple (By.XX, "value")
            text: The text to wait for
            timeout: Custom timeout in seconds (overrides default)
            message: Custom error message for TimeoutException

        Returns:
            bool: True if text is present

        Raises:
            TimeoutException: If text doesn't appear within timeout
        """
        wait_timeout = timeout if timeout is not None else self.timeout
        error_message = (
            message
            if message
            else f"Text '{text}' not present in element {locator} after {wait_timeout} seconds"
        )

        try:
            logger.debug(
                f"Waiting for text '{text}' to be present in element {locator}"
            )
            result = WebDriverWait(self.driver, wait_timeout).until(
                EC.text_to_be_present_in_element(locator, text)
            )
            logger.debug(f"Text '{text}' is now present in element {locator}")
            return result
        except TimeoutException:
            logger.error(error_message)
            raise TimeoutException(error_message)

    def wait_for_url_contains(self, text, timeout=None, message=None):
        """
        Wait for the URL to contain specific text.

        Args:
            text: Text to search for in URL
            timeout: Custom timeout in seconds (overrides default)
            message: Custom error message for TimeoutException

        Returns:
            bool: True if condition is met
        """
        wait_timeout = timeout if timeout is not None else self.timeout
        error_message = (
            message
            if message
            else f"URL did not contain '{text}' after {wait_timeout} seconds"
        )

        try:
            return WebDriverWait(self.driver, wait_timeout).until(EC.url_contains(text))
        except TimeoutException:
            logger.error(error_message)
            current_url = self.driver.current_url
            logger.error(f"Current URL: {current_url}")
            raise TimeoutException(error_message)

    def wait_for_element_visible(self, locator, timeout=None, message=None):
        """
        Enhanced wait for an element to be visible on the page.
        First waits for presence, then for visibility for a more robust approach.

        Args:
            locator: Element locator tuple (By.XX, "value")
            timeout: Custom timeout in seconds (overrides default)
            message: Custom error message for TimeoutException

        Returns:
            WebElement: The element once visible

        Raises:
            TimeoutException: If element doesn't become visible within timeout
        """
        wait_timeout = timeout if timeout is not None else self.timeout
        error_message = (
            message
            if message
            else f"Element {locator} not visible after {wait_timeout} seconds"
        )

        try:
            # First, wait for the element to be present in the DOM
            logger.debug(f"Waiting for element {locator} to be present in DOM")
            WebDriverWait(self.driver, wait_timeout).until(
                EC.presence_of_element_located(locator)
            )

            # Then, wait for it to be visible
            logger.debug(f"Waiting for element {locator} to be visible")
            element = WebDriverWait(self.driver, wait_timeout).until(
                EC.visibility_of_element_located(locator)
            )
            logger.debug(f"Element {locator} is now visible")
            return element
        except TimeoutException:
            logger.error(error_message)

            # Remove the problematic take_screenshot code
            # Just log the error without taking a screenshot
            logger.error(f"Element not found: {locator}")
            raise

    def wait_for_element_to_disappear(self, locator, timeout=None, message=None):
        """
        Wait for an element to disappear from the DOM or become invisible.

        Args:
            locator: Element locator tuple (By.XX, "value")
            timeout: Custom timeout in seconds (overrides default)
            message: Custom error message for TimeoutException

        Returns:
            bool: True if element is no longer visible/present

        Raises:
            TimeoutException: If element remains visible within timeout
        """
        wait_timeout = timeout if timeout is not None else self.timeout
        error_message = (
            message
            if message
            else f"Element {locator} still visible after {wait_timeout} seconds"
        )

        try:
            logger.debug(f"Waiting for element {locator} to disappear")
            result = WebDriverWait(self.driver, wait_timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            logger.debug(f"Element {locator} has disappeared")
            return result
        except TimeoutException:
            logger.error(error_message)
            raise TimeoutException(error_message)

    def wait_for_attribute_value(
        self, locator, attribute_name, value, timeout=None, message=None
    ):
        """
        Wait for an element's attribute to have a specific value.

        Args:
            locator: Element locator tuple (By.XX, "value")
            attribute_name: Name of the attribute to check
            value: Expected attribute value
            timeout: Custom timeout in seconds (overrides default)
            message: Custom error message for TimeoutException

        Returns:
            bool: True if attribute has the expected value

        Raises:
            TimeoutException: If attribute doesn't have expected value within timeout
        """
        wait_timeout = timeout if timeout is not None else self.timeout
        error_message = (
            message
            if message
            else f"Attribute '{attribute_name}' of element {locator} does not have value '{value}' after {wait_timeout} seconds"
        )

        def _check_attribute_value(driver):
            try:
                element = driver.find_element(*locator)
                actual_value = element.get_attribute(attribute_name)
                return actual_value == value
            except:
                return False

        try:
            logger.debug(
                f"Waiting for attribute '{attribute_name}' of element {locator} to have value '{value}'"
            )
            result = WebDriverWait(self.driver, wait_timeout).until(
                _check_attribute_value
            )
            logger.debug(
                f"Attribute '{attribute_name}' of element {locator} now has value '{value}'"
            )
            return result
        except TimeoutException:
            logger.error(error_message)
            raise TimeoutException(error_message)


# Example usage
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    from pulseq.utilities.driver_manager import initialize_driver

    driver = initialize_driver()
    wait_utils = WaitUtils(driver)

    try:
        driver.get("https://www.example.com")
        # Wait for page title element to be visible
        title_element = wait_utils.wait_for_element_visible((By.TAG_NAME, "h1"))
        print(f"Page title: {title_element.text}")
    finally:
        driver.quit()
