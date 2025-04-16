# tests/test_login.py

import pytest

from framework.page_objects.login_page import LoginPage
from framework.utilities.driver_manager import initialize_driver, quit_driver


@pytest.fixture(scope="function")
def driver():
    driver = initialize_driver(headless=True)
    yield driver
    quit_driver(driver)


def test_valid_login(driver):
    # Launch the web app
    driver.get("http://example.com/login")

    # Use the page object to perform actions
    login_page = LoginPage(driver)
    login_page.login("testuser", "securepassword")

    # Implement your custom assertions here
    assert (
        "dashboard" in driver.current_url
    ), "User did not navigate to dashboard upon login"
