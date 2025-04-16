# Test Automation Framework for Web Applications

This project is a modular test automation framework for web applications, designed using Python and Selenium. It leverages SOLID principles to ensure maintainability and reusability while integrating with GitHub Actions for continuous testing.

## Features

- **Modular Architecture:** Custom libraries and utilities for driver management, logging, and assertions.
- **Page Object Model:** Organized test code using page objects.
- **CI/CD Integration:** Automated testing with GitHub Actions and rich reporting with Allure.
- **Flexible Configuration:** Centralized configuration with default parameters.

## Setup & Usage

1. **Clone the repository:**

   ```bash
   git clone https://github.com/uelkerd/test-automation-framework.git
   cd test-automation-framework

   ```

2. **Create and activate a virtual environment:**

   ```python3 -m venv venv
   source venv/bin/activate

   ```

3. **Install dependencies:**

   ```pip install -r requirements.txt

   ```

4. **Run tests:**

   ```pytest

   ```

5. **Generate Allure Report:**

   ```python framework/reporting.py

   ```

For more details, see our documentation and architecture overview.
