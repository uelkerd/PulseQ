# Test Automation Framework Usage Guide

This document provides detailed instructions for using the test automation framework, including setup, configuration, test execution, and reporting.

## Setting Up the Environment

1. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install the Framework**

   ```bash
   pip install -r requirements.txt
   ```

## Running Tests

### Basic Test Execution

To run all tests:

```bash
pytest tests/
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
pytest tests/ -n auto
```

### Generating Reports

```bash
pytest tests/ --html=reports/report.html
```

## Using Framework Utilities

### Configuration

Create a `config.json` file in your project root:

```json
{
  "browser": "chrome",
  "headless": true,
  "implicit_wait": 10,
  "explicit_wait": 20,
  "base_url": "https://example.com",
  "screenshot_dir": "screenshots",
  "log_level": "INFO"
}
```

You can override these settings using environment variables:

```bash
export PULSEQ_BROWSER=firefox
export PULSEQ_HEADLESS=false
export PULSEQ_BASE_URL=https://staging.example.com
```

### Logger Setup

```python
from pulseq.utilities.logger import setup_logger

logger = setup_logger(__name__)
logger.info("Test started")
logger.error("Test failed")
```

### Screenshot Utilities

```python
from pulseq.utilities.misc_utils import MiscUtils

# Take screenshot
MiscUtils.take_screenshot(driver, "login_page")

# Take screenshot with timestamp
MiscUtils.take_screenshot_with_timestamp(driver, "error_state")
```

### Test Base Class

```python
from pulseq.core import TestBase

class TestLogin(TestBase):
    def test_successful_login(self):
        self.driver.get(self.config.base_url)
        # Test implementation
```

### Page Objects

```python
from pulseq.core import BasePage
from selenium.webdriver.common.by import By

class LoginPage(BasePage):
    # Locators
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-btn")

    def login(self, username, password):
        self.elements.send_keys(self.USERNAME_INPUT, username)
        self.elements.send_keys(self.PASSWORD_INPUT, password)
        self.elements.click_element(self.LOGIN_BUTTON)
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
python -m framework.core --tests tests/test_login.py --parallel 4

# Run tests without generating reports
python -m framework.core --tests tests/test_login.py --no-report

# Only collect tests without executing them
python -m framework.core --collect-only --tests tests/
```

## Continuous Integration

The framework integrates with GitHub Actions. See the `.github/workflows/ci.yml` file for the CI configuration.

To run the workflow manually:

1. Go to the Actions tab in your GitHub repository
2. Select the "Test Automation Framework CI" workflow
3. Click "Run workflow"
4. Select the environment and click "Run workflow"
