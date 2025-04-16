# Troubleshooting Guide

This guide addresses common issues you might encounter when using the test automation framework and provides solutions to resolve them.

## Table of Contents
- [WebDriver Issues](#webdriver-issues)
- [Test Failures](#test-failures)
- [Configuration Problems](#configuration-problems)
- [Timing Issues](#timing-issues)
- [Reporting Problems](#reporting-problems)
- [Environment Setup Issues](#environment-setup-issues)
- [CI/CD Pipeline Errors](#cicd-pipeline-errors)

## WebDriver Issues

### WebDriver Not Found

**Symptoms**:
- Error: `WebDriverException: Message: 'chromedriver' executable needs to be in PATH`
- Tests fail to start with driver initialization errors

**Solutions**:
1. Make sure you've installed the framework with all dependencies:
   ```bash
   pip install -e .
   ```

2. Verify that webdriver-manager is correctly installed:
   ```bash
   pip install webdriver-manager
   ```

3. If using a custom WebDriver path, check that the path is correct in your configuration.

4. For manual driver installation, ensure the driver version matches your browser version.

### Browser Crashes During Test Execution

**Symptoms**:
- Browser closes unexpectedly during test execution
- `WebDriverException: Message: disconnected: not connected to DevTools`

**Solutions**:
1. Update your browser to the latest version
2. Update WebDriver to match your browser version
3. Increase timeout values in the WebDriver initialization
4. Add additional Chrome options for stability:
   ```python
   options.add_argument("--no-sandbox")
   options.add_argument("--disable-dev-shm-usage")
   options.add_argument("--disable-gpu")
   ```

### WebDriver Session Times Out

**Symptoms**:
- Tests take too long to start
- Timeout errors when initializing WebDriver

**Solutions**:
1. Check your network connection
2. Verify that firewall or antivirus is not blocking the WebDriver
3. Try increasing the timeout values in `driver_manager.py`
4. If running in CI/CD, ensure the build agent has sufficient resources

## Test Failures

### Element Not Found Errors

**Symptoms**:
- `NoSuchElementException`
- Tests fail when trying to interact with elements

**Solutions**:
1. Check if selectors have changed in the application under test
2. Use the `wait_utils.py` module for proper explicit waits:
   ```python
   wait_utils = WaitUtils(driver)
   element = wait_utils.wait_for_element_visible(locator)
   ```
3. Verify that the test is running against the correct version of the application
4. Update page object selectors if the UI has changed

### Stale Element Reference Exceptions

**Symptoms**:
- `StaleElementReferenceException: Message: stale element reference: element is not attached to the page document`

**Solutions**:
1. Use the retry mechanism when interacting with elements that might become stale:
   ```python
   @retry(max_attempts=3, delay=1, backoff=2)
   def click_element_with_retry(element_utils, locator):
       element_utils.click_element(locator)
   ```
2. Re-find elements before each interaction rather than caching them
3. Use wait utilities to ensure the page has fully loaded before interacting with elements

### Tests Pass Locally But Fail in CI

**Symptoms**:
- Tests run successfully on your local machine but fail in CI environment

**Solutions**:
1. Ensure the CI environment is using the same browser version
2. Add more logging to troubleshoot environment-specific issues
3. Check for screen resolution differences (add `--window-size=1920,1080` to WebDriver options)
4. Verify that all required environment variables are set in CI
5. Examine screenshots captured during CI test runs

## Configuration Problems

### Environment Variables Not Loaded

**Symptoms**:
- Default configurations are used instead of environment-specific ones
- `KeyError` when trying to access environment variables

**Solutions**:
1. Ensure `.env` file exists in the project root (if using python-dotenv)
2. Check environment variable names match what the code expects
3. Verify that environment variables are set in your CI/CD pipeline settings
4. Use explicit file path for config files:
   ```python
   config = load_config(os.path.join(os.path.dirname(__file__), "../config.json"))
   ```

### Config File Not Found

**Symptoms**:
- `FileNotFoundError: [Errno 2] No such file or directory: 'config.json'`

**Solutions**:
1. Check that the config file exists in the expected location
2. Use absolute paths when loading config files
3. Create a default config if the file doesn't exist:
   ```python
   if not os.path.exists(config_file):
       # Create default config
       with open(config_file, 'w') as f:
           json.dump(default_config, f)
   ```

## Timing Issues

### Tests Fail Due to Timeouts

**Symptoms**:
- `TimeoutException: Message: timeout: Timed out receiving message from renderer`
- Actions taking too long to complete

**Solutions**:
1. Increase timeout values in wait utilities:
   ```python
   wait_utils = WaitUtils(driver, timeout=30)  # Increase from default 10s
   ```
2. Use retry mechanism for flaky operations:
   ```python
   @retry(max_attempts=5, delay=2, backoff=2)
   def flaky_operation():
       # your code here
   ```
3. Check application performance - slow response times might require longer timeouts
4. Optimize test code to reduce unnecessary waits

### Tests Run Too Slowly

**Symptoms**:
- Test execution takes too much time
- CI pipeline timeouts

**Solutions**:
1. Run tests in parallel using pytest-xdist:
   ```bash
   pytest -n 4  # Run with 4 parallel processes
   ```
2. Optimize wait strategies (use explicit waits instead of sleep)
3. Use headless browser mode for faster execution:
   ```python
   options.add_argument("--headless")
   ```
4. Minimize browser instances by reusing the same session for multiple tests

## Reporting Problems

### Allure Reports Not Generated

**Symptoms**:
- No report generated after test execution
- Missing test results in Allure report

**Solutions**:
1. Ensure allure-pytest is installed:
   ```bash
   pip install allure-pytest
   ```
2. Verify that pytest is run with the allure option:
   ```bash
   pytest --alluredir=allure-results
   ```
3. Check that the allure command-line tool is installed:
   ```bash
   allure --version
   ```
4. Generate the report manually:
   ```bash
   allure generate allure-results -o allure-report --clean
   ```

### Missing Screenshots in Reports

**Symptoms**:
- Screenshots not attached to failed test reports

**Solutions**:
1. Ensure the screenshot function is called in test teardown or with pytest fixtures:
   ```python
   @pytest.hookimpl(tryfirst=True, hookwrapper=True)
   def pytest_runtest_makereport(item, call):
       outcome = yield
       report = outcome.get_result()
       if report.when == "call" and report.failed:
           driver = item.funcargs.get("driver")
           if driver:
               allure.attach(
                   driver.get_screenshot_as_png(),
                   name="screenshot",
                   attachment_type=allure.attachment_type.PNG
               )
   ```
2. Verify screenshot directory permissions
3. Check that the screenshot path in reports is correct

## Environment Setup Issues

### Virtual Environment Problems

**Symptoms**:
- Import errors
- Missing dependencies

**Solutions**:
1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Check that you're using the correct Python version:
   ```bash
   python --version
   ```

### Python Package Conflicts

**Symptoms**:
- Dependency conflicts during installation
- `ImportError` despite packages being installed

**Solutions**:
1. Create a fresh virtual environment:
   ```bash
   python -m venv fresh_venv
   ```
2. Install packages one by one to identify conflicts
3. Use a requirements.txt with pinned versions:
   ```
   selenium==4.1.0
   pytest==7.0.0
   ```
4. Try using pip's dependency resolver:
   ```bash
   pip install --use-feature=2020-resolver -r requirements.txt
   ```

## CI/CD Pipeline Errors

### GitHub Actions Workflow Failures

**Symptoms**:
- GitHub Actions workflow fails
- Tests pass locally but fail in GitHub Actions

**Solutions**:
1. Check the workflow logs for specific error messages
2. Ensure all secrets and environment variables are properly set in GitHub repository settings
3. Verify that the workflow YAML syntax is correct
4. Use the GitHub Actions debugging feature by adding a tmate session:
   ```yaml
   - name: Setup tmate session
     uses: mxschmitt/action-tmate@v3
     if: ${{ failure() }}
   ```

### Headless Browser Issues in CI

**Symptoms**:
- Browser crashes in CI environment
- Screenshot errors in headless mode

**Solutions**:
1. Add additional Chrome options for CI environments:
   ```python
   options.add_argument("--no-sandbox")
   options.add_argument("--disable-dev-shm-usage")
   options.add_argument("--disable-gpu")
   options.add_argument("--window-size=1920,1080")
   ```
2. Use a Docker container with pre-installed browsers for CI runs
3. Try using Firefox instead of Chrome for CI execution:
   ```python
   from selenium.webdriver.firefox.options import Options as FirefoxOptions
   options = FirefoxOptions()
   options.add_argument("--headless")
   ```

If you encounter an issue not covered in this guide, please check the logs for detailed error messages and consider opening an issue on the project's GitHub repository.