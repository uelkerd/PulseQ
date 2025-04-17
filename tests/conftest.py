import os
import json
import pytest
import yaml
from pulseq.utilities.driver_manager import initialize_driver, quit_driver
from pulseq.utilities.logger import setup_logger

logger = setup_logger("conftest")

def pytest_configure(config):
    """Create test results directories if they don't exist."""
    os.makedirs("test_results/metrics", exist_ok=True)
    os.makedirs("test_results/logs", exist_ok=True)
    os.makedirs("test_data", exist_ok=True)

@pytest.fixture(scope="session")
def config():
    """Load test configuration from config.yaml."""
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def test_data():
    """Initialize test data."""
    products = [
        {"id": 1, "name": "Laptop", "price": 999.99, "quantity": 1},
        {"id": 2, "name": "Smartphone", "price": 499.99, "quantity": 2},
        {"id": 3, "name": "Headphones", "price": 129.99, "quantity": 1},
    ]

    shipping_methods = [
        {"id": 1, "name": "Standard", "price": 5.99, "days": "3-5"},
        {"id": 2, "name": "Express", "price": 15.99, "days": "1-2"},
        {"id": 3, "name": "Next Day", "price": 29.99, "days": "1"},
    ]

    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "address": "123 Test Street",
        "city": "Test City",
        "state": "TS",
        "zip": "12345",
        "country": "Test Country",
        "card_number": "4111111111111111",
        "card_expiry": "12/25",
        "card_cvv": "123",
    }

    # Save test data to files
    with open("test_data/products.json", "w") as f:
        json.dump(products, f, indent=2)

    with open("test_data/shipping.json", "w") as f:
        json.dump(shipping_methods, f, indent=2)

    with open("test_data/user.json", "w") as f:
        json.dump(user_data, f, indent=2)

    return {
        "products": products,
        "shipping_methods": shipping_methods,
        "user_data": user_data
    }

@pytest.fixture
def driver(config):
    """Initialize WebDriver instance."""
    driver = initialize_driver(headless=config["test_settings"]["headless"])
    driver.implicitly_wait(config["test_settings"]["implicit_wait"])
    driver.set_page_load_timeout(config["test_settings"]["page_load_timeout"])
    driver.set_script_timeout(config["test_settings"]["script_timeout"])
    
    yield driver
    
    quit_driver(driver)

@pytest.fixture(autouse=True)
def test_logging(request):
    """Set up logging for each test."""
    logger.info(f"Starting test: {request.node.name}")
    yield
    logger.info(f"Finished test: {request.node.name}") 