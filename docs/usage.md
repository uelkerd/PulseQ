# Usage Instructions

This document provides detailed instructions for using the test automation framework, including setup, configuration, test execution, and reporting.

## Setting Up the Environment

1. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install the Framework**

   ```bash
   # Install the framework and its dependencies
   pip install -e .

   # For development with linting tools
   pip install -e ".[dev]"

   # For image comparison features
   pip install -e ".[image]"
   ```

## Running Tests

### Basic Test Execution

To run all tests:

```bash
pytest
```

To run specific tests:

```bash
# Run tests in a specific file
pytest tests/test_login.py

# Run tests with a specific marker
pytest -m "smoke"

# Run tests that match a specific name pattern
pytest -k "login"
```

### Parallel Test Execution

Run tests in parallel using pytest-xdist:

```bash
# Run with 4 parallel processes
pytest -n 4

# Auto-detect the number of CPUs and use all of them
pytest -n auto
```

### Reporting

Generate Allure reports:

```bash
# Run tests with Allure reporting
pytest --alluredir=allure-results

# Generate HTML report
allure generate allure-results -o allure-report --clean

# Serve the report on a local web server
allure serve allure-results
```

## Using Framework Utilities

### Driver Manager

```python
from pulseq.utilities.driver_manager import initialize_driver, quit_driver

# Initialize WebDriver
driver = initialize_driver(headless=True)

# Use the driver
driver.get("https://example.com")

# Quit driver when done
quit_driver(driver)
```

### Wait Utilities

```python
from pulseq.utilities.wait_utils import WaitUtils
from selenium.webdriver.common.by import By

wait_utils = WaitUtils(driver)

# Wait for element to be visible
element = wait_utils.wait_for_element_visible((By.ID, "username"))

# Wait for element to be clickable
button = wait_utils.wait_for_element_clickable((By.ID, "submit"))

# Wait for URL to contain specific text
wait_utils.wait_for_url_contains("dashboard")
```

### Elements Utilities

```python
from pulseq.utilities.elements_utils import ElementsUtils
from selenium.webdriver.common.by import By

elements_utils = ElementsUtils(driver)

# Click an element
elements_utils.click_element((By.ID, "submit-button"))

# Send keys to an element
elements_utils.send_keys((By.ID, "username"), "testuser", clear_first=True)

# Get text from an element
text = elements_utils.get_text((By.ID, "message"))

# Check if element is present
is_present = elements_utils.is_element_present((By.ID, "error-message"))
```

### Data Handler

```python
from pulseq.utilities.data_handler import DataHandler

data_handler = DataHandler()

# Load data from JSON file
users = data_handler.load_json_data("users.json")

# Generate random test data
random_users = data_handler.generate_test_data_set(5, {
    "username": "string",
    "email": "email",
    "age": "number"
})

# Save data to CSV
data_handler.save_csv_data(random_users, "users.csv")
```

### Performance Metrics

```python
from pulseq.utilities.performance_metrics import PerformanceMetrics, measure_performance

# Create metrics instance
metrics = PerformanceMetrics()

# Use decorator to measure test performance
@measure_performance(metrics)
def test_login():
    # Test code here
    pass

# After tests complete
metrics.finalize_metrics()
metrics.save_metrics()
report = metrics.generate_report()
```

## Configuring the Framework

### Configuration File

Create a `config.json` file in the project root:

```json
{
  "base_url": "http://example.com",
  "timeout": 30,
  "retry_attempts": 3,
  "browser": "chrome",
  "headless": true,
  "screenshot_on_failure": true
}
```

### Environment Variables

You can override configuration with environment variables:

```bash
# Set base URL
export BASE_URL="http://staging.example.com"

# Set timeout
export TIMEOUT=60

# Set browser
export BROWSER="firefox"
```

## Using Page Objects

Create page objects to represent your application pages:

```python
# page_objects/login_page.py
from selenium.webdriver.common.by import By

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_field = (By.ID, "username")
        self.password_field = (By.ID, "password")
        self.login_button = (By.ID, "login-button")

    def login(self, username, password):
        self.driver.find_element(*self.username_field).send_keys(username)
        self.driver.find_element(*self.password_field).send_keys(password)
        self.driver.find_element(*self.login_button).click()
```

In your tests:

```python
from page_objects.login_page import LoginPage

def test_login(driver):
    login_page = LoginPage(driver)
    login_page.login("testuser", "password")
    # Add assertions here
```

## Using Docker

Run tests with Docker:

```bash
# Build and run with Docker Compose
docker-compose up test-runner

# Run specific tests
docker-compose run test-runner pytest tests/test_login.py

# Generate and view Allure reports
docker-compose up allure
```

## Custom Command Line Interface

Use the framework's CLI:

```bash
# Run tests with custom options
python -m pulseq.core --tests tests/test_login.py --parallel 4

# Run tests without generating reports
python -m pulseq.core --tests tests/test_login.py --no-report

# Only collect tests without executing them
python -m pulseq.core --collect-only --tests tests/
```

## Continuous Integration

The framework integrates with GitHub Actions. See the `.github/workflows/ci.yml` file for the CI configuration.

To run the workflow manually:

1. Go to the Actions tab in your GitHub repository
2. Select the "Test Automation Framework CI" workflow
3. Click "Run workflow"
4. Select the environment and click "Run workflow"
