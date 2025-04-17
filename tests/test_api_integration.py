import json

import pytest
from selenium.webdriver.common.by import By

from pulseq.utilities.api_client import APIClient
from pulseq.utilities.driver_manager import initialize_driver, quit_driver
from pulseq.utilities.elements_utils import ElementsUtils
from pulseq.utilities.performance_metrics import PerformanceMetrics, measure_performance
from pulseq.utilities.wait_utils import WaitUtils

# Initialize performance metrics tracking
metrics = PerformanceMetrics()

# Test data - could also use the data_handler
API_BASE_URL = "https://reqres.in/api"
USER_DATA = {"name": "John Smith", "job": "Quality Engineer"}

# Add retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# JSON Schema for validation
USER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "job", "createdAt"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "job": {"type": "string"},
        "createdAt": {"type": "string"},
    },
}


@pytest.fixture
def api_client():
    """Fixture to create and return an API client."""
    client = APIClient(base_url=API_BASE_URL)
    client.set_retry_config(max_retries=MAX_RETRIES, retry_delay=RETRY_DELAY)
    return client


@measure_performance(metrics)
def test_api_get_users(api_client):
    """Test retrieving a list of users via API."""
    try:
        # Send GET request to retrieve users with retry
        response = api_client.get("users", params={"page": 1}, retry=True)

        # Validate response status code
        api_client.validate_status_code(response, 200)

        # Validate response contains expected data
        response_data = response.json()
        assert "data" in response_data, "Response should contain 'data' field"
        assert len(response_data["data"]) > 0, "Users list should not be empty"

        # Validate specific fields in the response
        first_user = response_data["data"][0]
        assert "id" in first_user, "User should have an ID"
        assert "email" in first_user, "User should have an email"
        assert "first_name" in first_user, "User should have a first name"
        assert "last_name" in first_user, "User should have a last name"
    except Exception as e:
        pytest.fail(f"API GET users test failed: {str(e)}")


@measure_performance(metrics)
def test_api_create_user(api_client):
    """Test creating a user via API."""
    try:
        # Send POST request to create user with retry
        response = api_client.post("users", json=USER_DATA, retry=True)

        # Validate response status code
        api_client.validate_status_code(response, 201)

        # Validate response contains expected data
        response_data = response.json()
        assert (
            response_data["name"] == USER_DATA["name"]
        ), "Name should match input data"
        assert response_data["job"] == USER_DATA["job"], "Job should match input data"
        assert "id" in response_data, "Response should contain an ID"
        assert (
            "createdAt" in response_data
        ), "Response should contain creation timestamp"

        # Validate response against JSON schema
        try:
            api_client.validate_json_schema(response, USER_SCHEMA)
        except ImportError:
            pytest.skip("jsonschema package not installed")
    except Exception as e:
        pytest.fail(f"API create user test failed: {str(e)}")


@measure_performance(metrics)
def test_api_update_user(api_client):
    """Test updating a user via API."""
    try:
        # First create a user with retry
        create_response = api_client.post("users", json=USER_DATA, retry=True)
        user_id = create_response.json()["id"]

        # Update data
        updated_data = {"name": "John Smith", "job": "Senior Quality Engineer"}

        # Send PUT request to update user with retry
        response = api_client.put(f"users/{user_id}", json=updated_data, retry=True)

        # Validate response status code
        api_client.validate_status_code(response, 200)

        # Validate response contains updated data
        response_data = response.json()
        assert response_data["job"] == updated_data["job"], "Job should be updated"
        assert "updatedAt" in response_data, "Response should contain update timestamp"
    except Exception as e:
        pytest.fail(f"API update user test failed: {str(e)}")


@pytest.fixture
def driver():
    """Initialize and quit the WebDriver for each test."""
    driver = initialize_driver(headless=True)
    yield driver
    quit_driver(driver)


@measure_performance(metrics)
def test_api_ui_integration(api_client, driver):
    """Test integration between API calls and UI verification."""
    try:
        # 1. Create a user via API with retry
        create_response = api_client.post("users", json=USER_DATA, retry=True)
        api_client.validate_status_code(create_response, 201)
        user_id = create_response.json()["id"]

        # 2. Navigate to a UI page that would display the user
        driver.get(f"{API_BASE_URL.replace('/api', '')}/users/{user_id}")

        # 3. Use pulseq utilities to verify UI elements
        wait_utils = WaitUtils(driver)
        elements_utils = ElementsUtils(driver)

        # Wait for page to load with increased timeout
        wait_utils.wait_for_element_visible(
            (By.CSS_SELECTOR, ".user-details"), timeout=20
        )

        # Verify user details are displayed correctly
        user_name = elements_utils.get_text((By.CSS_SELECTOR, ".user-name"))
        assert (
            USER_DATA["name"] in user_name
        ), f"Expected user name '{USER_DATA['name']}' not found in '{user_name}'"

        # 4. Clean up - delete the user via API with retry
        delete_response = api_client.delete(f"users/{user_id}", retry=True)
        api_client.validate_status_code(delete_response, 204)
    except Exception as e:
        pytest.fail(f"API UI integration test failed: {str(e)}")


def teardown_module(module):
    """Save and report performance metrics after all tests complete."""
    metrics.finalize_metrics()
    metrics.save_metrics()
    report = metrics.generate_report()
    print(f"Performance Report: {report['summary']}")
