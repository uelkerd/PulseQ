# tests/test_data_driven.py

import json
import os

import pytest
from selenium.webdriver.common.by import By

from framework.page_objects.login_page import LoginPage
from framework.utilities.data_handler import DataHandler
from framework.utilities.driver_manager import initialize_driver, quit_driver
from framework.utilities.elements_utils import ElementsUtils
from framework.utilities.logger import setup_logger
from framework.utilities.wait_utils import WaitUtils

# Set up logger
logger = setup_logger("test_data_driven")

# Test data
TEST_USERS = [
    {"username": "testuser1", "password": "password1", "expected_result": "success"},
    {"username": "invaliduser", "password": "wrongpass", "expected_result": "failure"},
    {"username": "testuser2", "password": "password2", "expected_result": "success"},
]


# Create a test data file for demonstration
def setup_module(module):
    """Setup function that runs once before all tests in the module."""
    # Create test data directory if it doesn't exist
    data_dir = "test_data"
    os.makedirs(data_dir, exist_ok=True)

    # Create users.json test data file
    with open(os.path.join(data_dir, "users.json"), "w") as f:
        json.dump(TEST_USERS, f)

    logger.info("Test data setup complete")


@pytest.fixture(scope="function")
def driver():
    """Fixture to initialize and quit the WebDriver for each test."""
    driver = initialize_driver(headless=True)
    logger.info("WebDriver initialized")
    yield driver
    quit_driver(driver)
    logger.info("WebDriver closed")


@pytest.fixture(scope="module")
def test_data():
    """Fixture to load test data from file."""
    data_handler = DataHandler()
    try:
        # Try to load data from file
        data = data_handler.load_json_data("users.json")
        logger.info(f"Loaded test data: {len(data)} users")
    except FileNotFoundError:
        # Fall back to hardcoded data if file doesn't exist
        logger.warning("Test data file not found, using default data")
        data = TEST_USERS
    return data


# Parameterized test using pytest parameterization
@pytest.mark.parametrize("user_data", TEST_USERS)
def test_login_parameterized(driver, user_data):
    """Test login functionality with different user credentials using pytest parameterization."""
    driver.get("http://example.com/login")
    logger.info(f"Testing with user: {user_data['username']}")

    login_page = LoginPage(driver)
    login_page.login(user_data["username"], user_data["password"])

    # Verify login result
    if user_data["expected_result"] == "success":
        # Use wait_utils to wait for the dashboard to load
        wait_utils = WaitUtils(driver)
        try:
            wait_utils.wait_for_url_contains("dashboard", timeout=5)
            logger.info(f"Login successful for user: {user_data['username']}")
            assert "dashboard" in driver.current_url, (
                "User should be redirected to dashboard after successful login"
            )
        except Exception as e:
            logger.error(f"Login failed unexpectedly: {e}")
            assert False, f"Login should succeed for user {user_data['username']}"
    else:
        # Check for error message
        elements_utils = ElementsUtils(driver)
        error_message_locator = (By.ID, "errorMessage")
        assert elements_utils.is_element_present(error_message_locator), (
            "Error message should be displayed for invalid login"
        )
        logger.info(
            f"Login correctly failed for invalid user: {user_data['username']}")


# Alternative test using test_data fixture
def test_login_with_fixture(driver, test_data):
    """Test login functionality with different user credentials using fixture data."""
    driver.get("http://example.com/login")

    login_page = LoginPage(driver)
    elements_utils = ElementsUtils(driver)
    wait_utils = WaitUtils(driver)

    # Test each user from the loaded test data
    for user in test_data:
        logger.info(f"Testing with user from fixture: {user['username']}")
        login_page.login(user["username"], user["password"])

        if user["expected_result"] == "success":
            try:
                wait_utils.wait_for_url_contains("dashboard", timeout=5)
                logger.info(f"Login successful for user: {user['username']}")
                assert "dashboard" in driver.current_url, (
                    "User should be redirected to dashboard after successful login"
                )
                # Navigate back to login page for next test
                driver.get("http://example.com/login")
            except Exception as e:
                logger.error(f"Login failed unexpectedly: {e}")
                assert False, f"Login should succeed for user {user['username']}"
        else:
            # Check for error message
            error_message_locator = (By.ID, "errorMessage")
            assert elements_utils.is_element_present(error_message_locator), (
                "Error message should be displayed for invalid login"
            )
            logger.info(
                f"Login correctly failed for invalid user: {user['username']}")
            # Clear form for next test
            driver.get("http://example.com/login")


# Test with dynamically generated test data
def test_login_with_generated_data(driver):
    """Test login with dynamically generated user data."""
    driver.get("http://example.com/login")

    # Generate random test data
    data_handler = DataHandler()
    random_users = data_handler.generate_test_data_set(
        2, {"username": "string", "password": "string",
            "expected_result": "string"}
    )

    # Set expected results for demonstration
    # First random user will "fail"
    random_users[0]["expected_result"] = "failure"
    # Second random user will "succeed"
    random_users[1]["expected_result"] = "success"

    login_page = LoginPage(driver)
    elements_utils = ElementsUtils(driver)
    wait_utils = WaitUtils(driver)

    # Test each generated user
    for user in random_users:
        logger.info(f"Testing with generated user: {user['username']}")
        login_page.login(user["username"], user["password"])

        if user["expected_result"] == "success":
            try:
                wait_utils.wait_for_url_contains("dashboard", timeout=5)
                logger.info(
                    f"Login successful for generated user: {user['username']}")
                assert "dashboard" in driver.current_url, (
                    "User should be redirected to dashboard after successful login"
                )
                # Navigate back to login page for next test
                driver.get("http://example.com/login")
            except Exception as e:
                logger.error(f"Login failed unexpectedly: {e}")
                assert False, (
                    f"Login should succeed for generated user {user['username']}"
                )
        else:
            # Check for error message
            error_message_locator = (By.ID, "errorMessage")
            assert elements_utils.is_element_present(error_message_locator), (
                "Error message should be displayed for invalid login"
            )
            logger.info(
                f"Login correctly failed for invalid generated user: {user['username']}"
            )
            # Clear form for next test
            driver.get("http://example.com/login")
