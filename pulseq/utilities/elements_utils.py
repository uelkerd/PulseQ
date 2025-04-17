# pulseq/utilities/elements_utils.py

from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select

from pulseq.utilities.logger import setup_logger
from pulseq.utilities.wait_utils import WaitUtils

# Set up module logger
logger = setup_logger("elements_utils")


class ElementsUtils:
    """
    Provides utility methods for interacting with web elements.
    Wraps Selenium WebElement interactions with better error handling and logging.
    """

    def __init__(self, driver, timeout=10):
        """
        Initialize the elements utility with a WebDriver instance.

        Args:
            driver: Selenium WebDriver instance
            timeout: Default timeout in seconds
        """
        self.driver = driver
        self.timeout = timeout
        self.wait_utils = WaitUtils(driver, timeout)

    def click_element(self, locator, wait_for_clickable=True, timeout=None):
        """
        Click on an element with optional wait.

        Args:
            locator: Element locator tuple (By.XX, "value")
            wait_for_clickable: Whether to wait for element to be clickable first
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            None

        Raises:
            ElementNotInteractableException: If element is not clickable
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(f"Attempting to click element {locator}")

            if wait_for_clickable:
                element = self.wait_utils.wait_for_element_clickable(
                    locator, wait_timeout
                )
            else:
                element = self.driver.find_element(*locator)

            element.click()
            logger.debug(f"Clicked element {locator}")
        except ElementNotInteractableException as e:
            logger.error(f"Element {locator} not interactable: {e}")
            raise
        except Exception as e:
            logger.error(f"Error clicking element {locator}: {e}")
            raise

    def send_keys(self, locator, text, clear_first=True, timeout=None):
        """
        Send keys to an element with optional clearing.

        Args:
            locator: Element locator tuple (By.XX, "value")
            text: Text to send
            clear_first: Whether to clear the field first
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            None
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(f"Sending text '{text}' to element {locator}")
            element = self.wait_utils.wait_for_element_visible(locator, wait_timeout)

            if clear_first:
                element.clear()

            element.send_keys(text)
            logger.debug(f"Sent text to element {locator}")
        except Exception as e:
            logger.error(f"Error sending text to element {locator}: {e}")
            raise

    def get_text(self, locator, timeout=None):
        """
        Get text from an element.

        Args:
            locator: Element locator tuple (By.XX, "value")
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            str: Text content of the element
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(f"Getting text from element {locator}")
            element = self.wait_utils.wait_for_element_visible(locator, wait_timeout)
            text = element.text
            logger.debug(f"Got text '{text}' from element {locator}")
            return text
        except Exception as e:
            logger.error(f"Error getting text from element {locator}: {e}")
            raise

    def get_attribute(self, locator, attribute, timeout=None):
        """
        Get attribute value from an element.

        Args:
            locator: Element locator tuple (By.XX, "value")
            attribute: Attribute name to get
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            str: Attribute value
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(f"Getting attribute '{attribute}' from element {locator}")
            element = self.wait_utils.wait_for_element_visible(locator, wait_timeout)
            value = element.get_attribute(attribute)
            logger.debug(f"Got attribute value '{value}' from element {locator}")
            return value
        except Exception as e:
            logger.error(f"Error getting attribute from element {locator}: {e}")
            raise

    def select_dropdown_by_text(self, locator, text, timeout=None):
        """
        Select dropdown option by visible text.

        Args:
            locator: Element locator tuple (By.XX, "value")
            text: Visible text of the option to select
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            None
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(f"Selecting option '{text}' from dropdown {locator}")
            element = self.wait_utils.wait_for_element_visible(locator, wait_timeout)
            select = Select(element)
            select.select_by_visible_text(text)
            logger.debug(f"Selected option '{text}' from dropdown {locator}")
        except Exception as e:
            logger.error(f"Error selecting from dropdown {locator}: {e}")
            raise

    def select_dropdown_by_value(self, locator, value, timeout=None):
        """
        Select dropdown option by value.

        Args:
            locator: Element locator tuple (By.XX, "value")
            value: Value attribute of the option to select
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            None
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(
                f"Selecting option with value '{value}' from dropdown {locator}"
            )
            element = self.wait_utils.wait_for_element_visible(locator, wait_timeout)
            select = Select(element)
            select.select_by_value(value)
            logger.debug(
                f"Selected option with value '{value}' from dropdown {locator}"
            )
        except Exception as e:
            logger.error(f"Error selecting from dropdown {locator}: {e}")
            raise

    def select_dropdown_by_index(self, locator, index, timeout=None):
        """
        Select dropdown option by index.

        Args:
            locator: Element locator tuple (By.XX, "value")
            index: Index of the option to select (0-based)
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            None
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(f"Selecting option at index {index} from dropdown {locator}")
            element = self.wait_utils.wait_for_element_visible(locator, wait_timeout)
            select = Select(element)
            select.select_by_index(index)
            logger.debug(f"Selected option at index {index} from dropdown {locator}")
        except Exception as e:
            logger.error(f"Error selecting from dropdown {locator}: {e}")
            raise

    def hover_over_element(self, locator, timeout=None):
        """
        Hover over an element.

        Args:
            locator: Element locator tuple (By.XX, "value")
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            None
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(f"Hovering over element {locator}")
            element = self.wait_utils.wait_for_element_visible(locator, wait_timeout)
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            logger.debug(f"Hovered over element {locator}")
        except Exception as e:
            logger.error(f"Error hovering over element {locator}: {e}")
            raise

    def drag_and_drop(self, source_locator, target_locator, timeout=None):
        """
        Drag and drop from source element to target element.

        Args:
            source_locator: Source element locator tuple (By.XX, "value")
            target_locator: Target element locator tuple (By.XX, "value")
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            None
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(
                f"Performing drag and drop from {source_locator} to {target_locator}"
            )
            source_element = self.wait_utils.wait_for_element_visible(
                source_locator, wait_timeout
            )
            target_element = self.wait_utils.wait_for_element_visible(
                target_locator, wait_timeout
            )

            actions = ActionChains(self.driver)
            actions.drag_and_drop(source_element, target_element).perform()
            logger.debug("Performed drag and drop")
        except Exception as e:
            logger.error(f"Error performing drag and drop: {e}")
            raise

    def press_key(self, locator, key, timeout=None):
        """
        Press a specific key on an element.

        Args:
            locator: Element locator tuple (By.XX, "value")
            key: Key to press (from selenium.webdriver.common.keys.Keys)
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            None
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(f"Pressing key {key} on element {locator}")
            element = self.wait_utils.wait_for_element_visible(locator, wait_timeout)
            element.send_keys(key)
            logger.debug(f"Pressed key {key} on element {locator}")
        except Exception as e:
            logger.error(f"Error pressing key on element {locator}: {e}")
            raise

    def is_element_present(self, locator, timeout=1):
        """
        Check if element is present in the DOM.

        Args:
            locator: Element locator tuple (By.XX, "value")
            timeout: Time to wait before determining element is not present

        Returns:
            bool: True if element is present, False otherwise
        """
        try:
            logger.debug(f"Checking if element {locator} is present")
            self.wait_utils.wait_for_element_visible(locator, timeout)
            logger.debug(f"Element {locator} is present")
            return True
        except:
            logger.debug(f"Element {locator} is not present")
            return False

    def is_element_displayed(self, locator):
        """
        Check if element is displayed (visible to the user).

        Args:
            locator: Element locator tuple (By.XX, "value")

        Returns:
            bool: True if element is displayed, False otherwise
        """
        try:
            logger.debug(f"Checking if element {locator} is displayed")
            element = self.driver.find_element(*locator)
            result = element.is_displayed()
            logger.debug(
                f"Element {locator} is {'displayed' if result else 'not displayed'}"
            )
            return result
        except NoSuchElementException:
            logger.debug(f"Element {locator} does not exist in DOM")
            return False
        except Exception as e:
            logger.error(f"Error checking if element {locator} is displayed: {e}")
            return False

    def scroll_to_element(self, locator, timeout=None):
        """
        Scroll the page to bring an element into view.

        Args:
            locator: Element locator tuple (By.XX, "value")
            timeout: Custom timeout in seconds (overrides default)

        Returns:
            None
        """
        wait_timeout = timeout if timeout is not None else self.timeout

        try:
            logger.debug(f"Scrolling to element {locator}")
            # Try to find the element directly first
            try:
                element = self.driver.find_element(*locator)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", element
                )
                logger.debug(f"Scrolled to element {locator}")
                return element
            except Exception:
                # If direct find fails, try with waiting
                element = self.wait_utils.wait_for_element_visible(
                    locator, wait_timeout
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", element
                )
                logger.debug(f"Scrolled to element {locator} after waiting")
                return element
        except Exception as e:
            logger.error(f"Error scrolling to element {locator}: {e}")
            raise


# Example usage
if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    from pulseq.utilities.driver_manager import initialize_driver

    driver = initialize_driver()
    elements_utils = ElementsUtils(driver)

    try:
        driver.get("https://www.example.com")
        # Check if the heading is present
        if elements_utils.is_element_present((By.TAG_NAME, "h1")):
            # Get text from heading
            heading_text = elements_utils.get_text((By.TAG_NAME, "h1"))
            print(f"Heading text: {heading_text}")
    finally:
        driver.quit()
