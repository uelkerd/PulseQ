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
    return client


@measure_performance(metrics)
def test_api_get_users(api_client):
    """Test retrieving a list of users via API."""
    # Send GET request to retrieve users
    response = api_client.get("users", params={"page": 1})

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


@measure_performance(metrics)
def test_api_create_user(api_client):
    """Test creating a user via API."""
    # Send POST request to create user
    response = api_client.post("users", json=USER_DATA)

    # Validate response status code
    api_client.validate_status_code(response, 201)

    # Validate response contains expected data
    response_data = response.json()
    assert response_data["name"] == USER_DATA["name"], "Name should match input data"
    assert response_data["job"] == USER_DATA["job"], "Job should match input data"
    assert "id" in response_data, "Response should contain an ID"
    assert "createdAt" in response_data, "Response should contain creation timestamp"

    # Validate response against JSON schema
    try:
        api_client.validate_json_schema(response, USER_SCHEMA)
    except ImportError:
        pytest.skip("jsonschema package not installed")


@measure_performance(metrics)
def test_api_update_user(api_client):
    """Test updating a user via API."""
    # First create a user
    create_response = api_client.post("users", json=USER_DATA)
    user_id = create_response.json()["id"]

    # Update data
    updated_data = {"name": "John Smith", "job": "Senior Quality Engineer"}

    # Send PUT request to update user
    response = api_client.put(f"users/{user_id}", json=updated_data)

    # Validate response status code
    api_client.validate_status_code(response, 200)

    # Validate response contains updated data
    response_data = response.json()
    assert response_data["job"] == updated_data["job"], "Job should be updated"
    assert "updatedAt" in response_data, "Response should contain update timestamp"


@pytest.fixture
def driver():
    """Initialize and quit the WebDriver for each test."""
    driver = initialize_driver(headless=True)
    yield driver
    quit_driver(driver)


@measure_performance(metrics)
def test_api_ui_integration(api_client, driver):
    """Test integration between API calls and UI verification."""
    # 1. Create a user via API
    create_response = api_client.post("users", json=USER_DATA)
    api_client.validate_status_code(create_response, 201)
    user_id = create_response.json()["id"]

    # 2. Navigate to a UI page that would display the user
    driver.get(f"{API_BASE_URL.replace('/api', '')}/users/{user_id}")

    # 3. Use pulseq utilities to verify UI elements
    wait_utils = WaitUtils(driver)
    elements_utils = ElementsUtils(driver)

    # Wait for page to load
    wait_utils.wait_for_element_visible((By.CSS_SELECTOR, ".user-details"), timeout=10)

    # Verify user details are displayed correctly
    user_name = elements_utils.get_text((By.CSS_SELECTOR, ".user-name"))
    assert (
        USER_DATA["name"] in user_name
    ), f"Expected user name '{USER_DATA['name']}' not found in '{user_name}'"

    # 4. Clean up - delete the user via API
    delete_response = api_client.delete(f"users/{user_id}")
    api_client.validate_status_code(delete_response, 204)


def teardown_module(module):
    """Save and report performance metrics after all tests complete."""
    metrics.finalize_metrics()
    metrics.save_metrics()
    report = metrics.generate_report()
    print(f"Performance Report: {report['summary']}")
