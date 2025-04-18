import os
import json
import pytest
import yaml
from pulseq.utilities.driver_manager import initialize_driver, quit_driver
from pulseq.utilities.logger import setup_logger
from pulseq.utilities.performance_metrics import PerformanceMetrics
from pulseq.utilities.performance_analyzer import PerformanceAnalyzer

logger = setup_logger("conftest")
performance_analyzer = PerformanceAnalyzer()

def pytest_configure(config):
    """Create test results directories and configure parallel execution."""
    os.makedirs("test_results/metrics", exist_ok=True)
    os.makedirs("test_results/logs", exist_ok=True)
    os.makedirs("test_data", exist_ok=True)
    
    # Configure parallel execution
    if config.getoption('--dist') == 'no':
        config.option.dist = 'loadfile'
    if not config.getoption('--tx'):
        config.option.tx = ['popen//python=python']

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
    """Initialize WebDriver instance with resource cleanup."""
    driver = initialize_driver(headless=config["test_settings"]["headless"])
    driver.implicitly_wait(config["test_settings"]["implicit_wait"])
    driver.set_page_load_timeout(config["test_settings"]["page_load_timeout"])
    driver.set_script_timeout(config["test_settings"]["script_timeout"])
    
    yield driver
    
    # Cleanup resources
    driver.execute_script("window.performance.clearResourceTimings();")
    driver.execute_script("window.performance.clearMarks();")
    driver.execute_script("window.performance.clearMeasures();")
    quit_driver(driver)

@pytest.fixture
def metrics(request, config):
    """Initialize performance metrics collector with trend analysis."""
    metrics_file = os.path.join(config["metrics"]["output_dir"], config["metrics"]["default_filename"])
    metrics = PerformanceMetrics(metrics_file=metrics_file)
    
    yield metrics
    
    # Record metrics in analyzer
    test_name = request.node.name
    performance_analyzer.record_metrics(test_name, metrics.get_all_metrics())
    metrics.save_metrics()

@pytest.fixture(autouse=True)
def test_logging(request):
    """Set up logging for each test with performance monitoring."""
    logger.info(f"Starting test: {request.node.name}")
    yield
    logger.info(f"Finished test: {request.node.name}")

def pytest_sessionfinish(session, exitstatus):
    """Generate performance reports at the end of the test session."""
    performance_analyzer.save_run_metrics()
    performance_analyzer.generate_trend_plots()
    performance_analyzer.generate_report()
    
    # Check for regressions
    regressions = performance_analyzer.detect_regressions()
    if regressions:
        logger.warning("Performance regressions detected:")
        for reg in regressions:
            logger.warning(f"  {reg['test_name']} - {reg['metric_name']}: "
                         f"Current: {reg['current_value']:.2f}, "
                         f"Historical Mean: {reg['historical_mean']:.2f}")

def pytest_addoption(parser):
    """Add custom command line options for performance testing."""
    parser.addoption(
        "--performance-threshold",
        action="store",
        default=2.0,
        type=float,
        help="Number of standard deviations to consider as performance regression"
    ) 