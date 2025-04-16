# Architecture Overview

## Framework Components

- **Core Module:**  
  Manages test execution flow and configuration loading.

- **Configuration Module:**  
  Loads settings from JSON files and environment variables.

- **Utilities:**  
  - **Driver Manager:** Initializes and manages Selenium WebDriver instances.
  - **Logger:** Provides centralized logging for traceability.
  - **Assertions:** Custom assertions for more readable test failures.
  - **Retry:** A decorator for handling transient failures with retry logic.

- **Page Objects:**  
  Encapsulate web page interactions in reusable classes (e.g., LoginPage).

- **Reporting:**  
  Integrates with tools like Allure to generate comprehensive test reports.

## Diagram

Below is a simplified diagram representing module interactions:

```mermaid
graph TD;
    A[Core Module] --> B[Configuration];
    A --> C[Utilities];
    C --> D[Driver Manager];
    C --> E[Logger];
    C --> F[Retry];
    A --> G[Page Objects];
    A --> H[Reporting];
