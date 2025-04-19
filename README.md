# PulseQ Test Automation Framework

[![Enterprise CI/CD](https://github.com/uelkerd/PulseQ/actions/workflows/enterprise-ci.yml/badge.svg)](https://github.com/uelkerd/PulseQ/actions/workflows/enterprise-ci.yml)
[![CI](https://github.com/uelkerd/PulseQ/actions/workflows/ci.yml/badge.svg)](https://github.com/uelkerd/PulseQ/actions/workflows/ci.yml)
[![CodeQL Analysis](https://github.com/uelkerd/PulseQ/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/uelkerd/PulseQ/actions/workflows/codeql-analysis.yml)
[![Performance Monitoring](https://github.com/uelkerd/PulseQ/actions/workflows/performance-monitoring.yml/badge.svg)](https://github.com/uelkerd/PulseQ/actions/workflows/performance-monitoring.yml)

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Code Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen?style=for-the-badge)

## Overview

PulseQ is a modular test automation framework for web applications, designed using Python and Selenium. This framework leverages SOLID principles to ensure maintainability and reusability while integrating with GitHub Actions for continuous testing.

## Key Features

- **Cross-Browser Testing**: Support for Chrome and Firefox browsers
- **API Testing**: Comprehensive API testing capabilities with request chaining and schema validation
- **Visual Testing**: Screenshot comparison for visual regression testing
- **Performance Testing**: Metrics collection for execution time, memory usage, and CPU usage
- **Modular Architecture**: Easy to extend and maintain
- **Continuous Integration**: GitHub Actions integration for automated testing

## Project Structure

```text
PulseQ/
├── .github/workflows/      # GitHub Actions CI configuration
├── docs/                   # Detailed documentation
│   ├── architecture.md     # Architecture details and diagrams
│   ├── troubleshooting.md  # Troubleshooting guide
│   └── usage.md            # Usage instructions
├── pulseq/                 # Core framework components
│   ├── utilities/          # Utility modules
│   │   ├── api_client.py        # API testing utilities
│   │   ├── driver_manager.py    # WebDriver management
│   │   ├── visual_utils.py       # Visual testing utilities
│   │   ├── logger.py            # Centralized logging
│   │   ├── assertions.py        # Custom assertions
│   │   ├── wait_utils.py        # Wait utilities
│   │   ├── elements_utils.py    # Element interaction utilities
│   │   ├── data_handler.py      # Test data management
│   │   ├── retry.py             # Retry mechanism
│   │   ├── performance_metrics.py # Performance tracking
│   │   └── misc_utils.py        # Additional utilities
│   ├── page_objects/       # Page object classes
│   ├── config.py           # Configuration management
│   ├── core.py            # Core framework functionality
│   └── reporting.py        # Test reporting
├── tests/                  # Test cases
│   ├── api/              # API tests
│   ├── visual/           # Visual tests
│   └── performance/      # Performance tests
├── metrics/                # Performance metrics storage
├── Dockerfile              # Container definition
├── docker-compose.yml      # Container orchestration
├── requirements.txt        # Python dependencies
├── setup.py                # Package configuration
└── README.md               # Project overview
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Chrome or Firefox browser
- Java Runtime Environment (for Allure reporting)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/uelkerd/PulseQ.git
   cd PulseQ
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -e .
   ```

### Running Tests

#### Simple Test Execution

```bash
pytest
```

#### With Specific Test Path

```bash
pytest tests/test_login.py
```

#### With Allure Reporting

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

#### Using the Framework CLI

```bash
python -m pulseq.core --tests tests/test_e2e_checkout.py --parallel 2
```

## Usage Examples

### API Testing

```python
from pulseq.utilities.api_client import APIClient

# Initialize API client
client = APIClient("https://api.example.com")

# Make requests
response = client.get("/users")
assert response.status_code == 200

# Chain requests
user = client.post("/users", json={"name": "John"}).json()
client.get(f"/users/{user['id']}").validate_status_code(200)
```

### Visual Testing

```python
from pulseq.utilities.visual_utils import VisualTester

# Initialize visual tester
tester = VisualTester()

# Take and compare screenshots
screenshot = tester.take_screenshot(driver, "homepage")
matches, similarity = tester.compare_screenshots(screenshot, "baseline.png")
assert matches, f"Screenshots differ (similarity: {similarity})"
```

### Performance Testing

```python
from pulseq.utilities.performance_metrics import measure_performance

@measure_performance
def test_page_load(driver, metrics):
    driver.get("https://example.com")
    assert metrics.get_average("execution_time") < 5.0
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Selenium](https://www.selenium.dev/) for web automation
- [Pytest](https://docs.pytest.org/) for testing framework
- [GitHub Actions](https://github.com/features/actions) for CI/CD
