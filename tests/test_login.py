# tests/test_login.py

import pytest
import os
import tempfile
from selenium.webdriver.common.by import By
from pulseq.utilities.driver_manager import initialize_driver, quit_driver
from pulseq.page_objects.login_page import LoginPage


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
        </form>
        <script>
            document.getElementById('loginBtn').addEventListener('click', function() {
                if (document.getElementById('username').value === 'testuser' && 
                    document.getElementById('password').value === 'securepassword') {
                    window.location.href = 'dashboard.html';
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
    driver = initialize_driver(headless=True)
    yield driver
    quit_driver(driver)


def test_valid_login(driver, mock_html):
    # Launch the mock login page
    driver.get(mock_html)

    # Use the page object to perform actions
    login_page = LoginPage(driver)
    login_page.login("testuser", "securepassword")

    # Wait briefly for the page transition
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    WebDriverWait(driver, 3).until(EC.title_contains("Dashboard"))

    # Check that we're on the dashboard page
    assert (
        "dashboard" in driver.current_url.lower()
    ), "User did not navigate to dashboard upon login"
