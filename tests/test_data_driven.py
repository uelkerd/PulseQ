# tests/test_data_driven.py

import json
import os
import tempfile

import pytest
from selenium.webdriver.common.by import By

from pulseq.page_objects.login_page import LoginPage
from pulseq.utilities.data_handler import DataHandler
from pulseq.utilities.driver_manager import initialize_driver, quit_driver
from pulseq.utilities.elements_utils import ElementsUtils
from pulseq.utilities.logger import setup_logger
from pulseq.utilities.wait_utils import WaitUtils

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
def mock_html():
    """Create a temporary HTML file with login form for testing."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Login Page</title>
    </head>
    <body>
        <form id="loginForm">
            <input type="text" id="username" name="username" placeholder="Username">
            <input type="password" id="password" name="password" placeholder="Password">
            <button id="loginBtn" type="button">Login</button>
            <div id="errorMessage" style="display:none; color:red;">Invalid username or password</div>
        </form>
        <script>
            document.getElementById('loginBtn').addEventListener('click', function() {
                var username = document.getElementById('username').value;
                var password = document.getElementById('password').value;
                var errorMsg = document.getElementById('errorMessage');
                
                if ((username === 'testuser1' && password === 'password1') || 
                    (username === 'testuser2' && password === 'password2')) {
                    window.location.href = 'dashboard.html';
                } else {
                    errorMsg.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """

    # Create dashboard.html as well
    dashboard_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard</title>
    </head>
    <body>
        <h1>Welcome to the Dashboard</h1>
    </body>
    </html>
    """

    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create the login HTML file
    login_path = os.path.join(temp_dir, "login.html")
    with open(login_path, "w") as f:
        f.write(html_content)

    # Create the dashboard HTML file
    dashboard_path = os.path.join(temp_dir, "dashboard.html")
    with open(dashboard_path, "w") as f:
        f.write(dashboard_content)

    # Return the path to the login file
    yield "file://" + login_path

    # Clean up
    os.remove(login_path)
    os.remove(dashboard_path)
    os.rmdir(temp_dir)


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
def test_login_parameterized(driver, mock_html, user_data):
    """Test login functionality with different user credentials using pytest parameterization."""
    driver.get(mock_html)
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
def test_login_with_fixture(driver, mock_html, test_data):
    """Test login functionality with different user credentials using fixture data."""
    driver.get(mock_html)

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
                driver.get(mock_html)
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
            driver.get(mock_html)


# Test with dynamically generated test data
def test_login_with_generated_data(driver, mock_html):
    """Test login with dynamically generated user data."""
    driver.get(mock_html)

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
    random_users[1]["username"] = (
        "testuser1"  # Make sure second user matches success condition
    )
    random_users[1]["password"] = "password1"  # in the HTML mock

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
                driver.get(mock_html)
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
            driver.get(mock_html)
