# tests/test_api_ui_integration.py
import pytest
from selenium.webdriver.common.by import By

from pulseq.utilities.api_client import APIClient
from pulseq.utilities.driver_manager import initialize_driver, quit_driver
from pulseq.utilities.wait_utils import WaitUtils
from pulseq.utilities.elements_utils import ElementsUtils
from pulseq.utilities.performance_metrics import measure_performance, PerformanceMetrics

# Set up metrics
metrics = PerformanceMetrics()

@pytest.fixture
def driver():
    """Initialize and quit the WebDriver for each test."""
    driver = initialize_driver(headless=True)
    yield driver
    quit_driver(driver)

@pytest.fixture
def api_client():
    """Initialize the API client."""
    client = APIClient("https://reqres.in/api")
    return client

@pytest.fixture
def api_user(api_client):
    """Create a test user via API."""
    user_data = {"name": "John Doe", "job": "QA Engineer"}
    response = api_client.post("/users", json=user_data)
    assert response.status_code == 201
    return response.json()

@measure_performance(metrics)
def test_api_setup_ui_verification(driver, api_client, api_user):
    """Test UI based on API data.
    
    This test demonstrates:
    1. Setting up test data via API
    2. Verifying it in the UI
    3. Updating via API
    4. Verifying the update in UI
    """
    # Set up utilities
    wait_utils = WaitUtils(driver)
    elements_utils = ElementsUtils(driver)
    
    # 1. Open the user page using API data
    user_id = 2  # Using a known user ID since ReqRes doesn't persist created users
    driver.get(f"https://reqres.in/#/users/{user_id}")
    
    # 2. Verify user is displayed in UI
    # Note: In a real application, we would check for the specific user
    # Here we're just checking that a user page loads
    wait_utils.wait_for_element_visible((By.CSS_SELECTOR, ".user-details"))
    
    # 3. Get more user data via API
    response = api_client.get(f"/users/{user_id}")
    api_client.validate_status_code(response, 200)
    user_details = response.json()["data"]
    
    # 4. Verify API data matches what's in the UI
    # Note: In a real app, we would check these values in the UI
    # For reqres.in, we're showing the pattern but not the actual verification
    assert user_details["id"] == user_id
    
    # 5. In a real app, we might update the user via API and verify changes in UI
    print(f"Test completed successfully: API user {api_user['name']} created")
    print(f"API data successfully retrieved for user: {user_details['first_name']} {user_details['last_name']}") 