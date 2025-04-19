# tests/api/test_reqres_api.py
import json
import logging

import pytest
from jsonschema import validate

from pulseq.utilities.api_client import APIClient
from pulseq.utilities.logger import setup_logger
from pulseq.utilities.performance_metrics import PerformanceMetrics, measure_performance
from pulseq.utilities.retry import retry

# Set up logger and metrics
logger = setup_logger("api_tests")
metrics = PerformanceMetrics()

# Base URL for ReqRes API
BASE_URL = "https://reqres.in/api"

# JSON Schemas for validation
USER_SCHEMA = {
    "type": "object",
    "required": ["id", "email", "first_name", "last_name", "avatar"],
    "properties": {
        "id": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "avatar": {"type": "string", "format": "uri"},
    },
}

USERS_LIST_SCHEMA = {
    "type": "object",
    "required": ["page", "per_page", "total", "total_pages", "data"],
    "properties": {
        "page": {"type": "integer"},
        "per_page": {"type": "integer"},
        "total": {"type": "integer"},
        "total_pages": {"type": "integer"},
        "data": {"type": "array", "items": USER_SCHEMA},
    },
}

CREATE_USER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "job", "createdAt"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "job": {"type": "string"},
        "createdAt": {"type": "string"},
    },
}


# Fixtures
@pytest.fixture
def api_client():
    """Initialize the API client with base URL."""
    client = APIClient(BASE_URL, verify_ssl=False)
    logger.info(f"Initialized API client for {BASE_URL}")
    return client


@pytest.fixture
def created_user(api_client):
    """Create a test user and yield the user data for tests.
    Clean up by deleting the user after tests complete."""
    # Create user
    user_data = {"name": "John Doe", "job": "QA Engineer"}
    response = api_client.post("/users", json=user_data)

    # Verify creation was successful
    assert response.status_code == 201, f"Failed to create test user: {response.text}"
    user = response.json()
    logger.info(f"Created test user with ID: {user['id']}")

    # Yield user for test use
    yield user

    # Cleanup - delete user (Note: ReqRes doesn't actually delete the resource,
    # but this demonstrates the pattern)
    response = api_client.delete(f"/users/{user['id']}")
    assert response.status_code in [
        200,
        204,
    ], f"Failed to delete test user: {response.text}"
    logger.info(f"Deleted test user with ID: {user['id']}")


# Test cases
@measure_performance(metrics)
def test_get_users_list(api_client):
    """Test getting a list of users with pagination."""
    # Get users - page 1
    response = api_client.get("/users", params={"page": 1})
    api_client.validate_status_code(response, 200)

    # Validate response data
    data = response.json()
    validate(instance=data, schema=USERS_LIST_SCHEMA)

    # Verify pagination
    assert data["page"] == 1
    assert len(data["data"]) > 0
    assert data["total_pages"] >= 1

    logger.info(f"Successfully retrieved {len(data['data'])} users")


@measure_performance(metrics)
def test_get_single_user(api_client):
    """Test getting details of a single user."""
    # Get a specific user (ID 2 is known to exist in the system)
    response = api_client.get("/users/2")
    api_client.validate_status_code(response, 200)

    # Validate response structure
    data = response.json()
    assert "data" in data
    validate(instance=data["data"], schema=USER_SCHEMA)

    # Check specific user details
    user = data["data"]
    assert user["id"] == 2
    assert user["email"].endswith("@reqres.in")
    assert user["first_name"]
    assert user["last_name"]

    logger.info(
        f"Successfully retrieved user: {user['first_name']} {user['last_name']}"
    )


@measure_performance(metrics)
def test_create_user(api_client):
    """Test creating a new user."""
    # User data to create
    user_data = {"name": "Jane Smith", "job": "Software Engineer"}

    # Create user
    response = api_client.post("/users", json=user_data)
    api_client.validate_status_code(response, 201)

    # Validate response
    created_user = response.json()
    validate(instance=created_user, schema=CREATE_USER_SCHEMA)

    # Verify user details were saved
    assert created_user["name"] == user_data["name"]
    assert created_user["job"] == user_data["job"]
    assert "id" in created_user
    assert "createdAt" in created_user

    logger.info(f"Successfully created user with ID: {created_user['id']}")


@measure_performance(metrics)
def test_update_user(api_client, created_user):
    """Test updating an existing user."""
    # Updated user data
    updated_data = {"name": created_user["name"], "job": "Senior QA Engineer"}

    # Update user with PUT (full update)
    response = api_client.put(f"/users/{created_user['id']}", json=updated_data)
    api_client.validate_status_code(response, 200)

    # Verify response
    update_response = response.json()
    assert update_response["job"] == updated_data["job"]
    assert "updatedAt" in update_response

    # Partial update with PATCH
    patch_data = {"job": "Principal QA Engineer"}
    response = api_client.patch(f"/users/{created_user['id']}", json=patch_data)
    api_client.validate_status_code(response, 200)

    # Verify response
    patch_response = response.json()
    assert patch_response["job"] == patch_data["job"]
    assert "updatedAt" in patch_response

    logger.info("Successfully performed both full and partial updates")


@measure_performance(metrics)
@retry(max_attempts=3, delay=1, backoff=2)
def test_login_authentication(api_client):
    """Test authentication endpoints with retry mechanism."""
    # Successful login
    credentials = {"email": "eve.holt@reqres.in", "password": "cityslicka"}
    response = api_client.post("/login", json=credentials)
    api_client.validate_status_code(response, 200)

    auth_response = response.json()
    assert "token" in auth_response
    token = auth_response["token"]

    # Unsuccessful login (missing password)
    bad_credentials = {"email": "eve.holt@reqres.in"}
    response = api_client.post("/login", json=bad_credentials)
    api_client.validate_status_code(response, 400)

    error_response = response.json()
    assert "error" in error_response
    assert error_response["error"] == "Missing password"

    logger.info("Successfully tested authentication endpoints")


@measure_performance(metrics)
def test_api_workflow(api_client):
    """Test a complete API workflow combining multiple operations."""
    # 1. Get list of users
    response = api_client.get("/users", params={"page": 1})
    api_client.validate_status_code(response, 200)
    initial_users = response.json()

    # 2. Create new user
    user_data = {"name": "Workflow Test User", "job": "Integration Tester"}
    response = api_client.post("/users", json=user_data)
    api_client.validate_status_code(response, 201)
    new_user = response.json()

    # 3. Update the user
    update_data = {"name": new_user["name"], "job": "Senior Integration Tester"}
    response = api_client.put(f"/users/{new_user['id']}", json=update_data)
    api_client.validate_status_code(response, 200)

    # 4. Get user details (Note: ReqRes doesn't actually store the created users,
    # so we can't retrieve them, but this shows the pattern)

    # 5. Delete the user
    response = api_client.delete(f"/users/{new_user['id']}")
    api_client.validate_status_code(response, 204)

    logger.info("Successfully completed multi-step API workflow")


def test_login_success(api_client):
    """Test successful login with valid credentials."""
    credentials = {
        "email": "test_user@example.com",
        "password": "test_password_123"
    }
    response = api_client.post("/login", json=credentials)
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_failure(api_client):
    """Test login failure with invalid credentials."""
    credentials = {
        "email": "test_user@example.com",
        "password": "wrong_password"
    }
    response = api_client.post("/login", json=credentials)
    assert response.status_code == 400
    assert "error" in response.json()


def test_login_missing_password(api_client):
    """Test login failure with missing password."""
    credentials = {"email": "test_user@example.com"}
    response = api_client.post("/login", json=credentials)
    assert response.status_code == 400
    assert response.json()["error"] == "Missing password"


# Teardown
def teardown_module(module):
    """Generate performance report after all tests complete."""
    metrics.finalize_metrics()
    report = metrics.generate_report()
    logger.info(f"Test performance metrics: {report['summary']}")
