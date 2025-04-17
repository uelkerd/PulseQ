# pulseq/core.py
import argparse
import time
from datetime import datetime
from pathlib import Path

import pytest

from pulseq.config import load_config
from pulseq.reporting import generate_allure_report
from pulseq.utilities.logger import setup_logger

# Set up module logger
logger = setup_logger("core")


class FrameworkCore:
    """
    Core class that serves as the main entry point for the test automation framework.
    Handles configuration loading, test execution, reporting, and metrics tracking.
    """

    def __init__(self, config_file=None):
        """
        Initialize the framework core.

        Args:
            config_file: Path to the configuration file (optional)
        """
        self.start_time = time.time()
        self.config = load_config(config_file)
        logger.info("Framework initialized with configuration")
        logger.debug(f"Configuration: {self.config}")

        # Ensure required directories exist
        self._ensure_directories()

    @staticmethod
    def _ensure_directories():
        """Create required directories if they don't exist."""
        directories = ["screenshots", "logs", "allure-results", "test_data"]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")

    def run_tests(self, test_path=None, markers=None, parallel=1, report=True):
        """
        Run tests using pytest.

        Args:
            test_path: Path to test files or directories
            markers: Pytest markers to filter tests
            parallel: Number of parallel processes (0 = auto)
            report: Whether to generate a report after test execution

        Returns:
            int: Pytest exit code
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Starting test execution at {timestamp}")

        # Build pytest arguments
        pytest_args = []

        # Add test path if specified
        if test_path:
            pytest_args.append(test_path)

        # Add markers if specified
        if markers:
            pytest_args.append(f"-m={markers}")

        # Add default pytest arguments
        pytest_args.extend(["--alluredir=allure-results", "-v"])

        # Add parallel execution if specified
        if parallel > 1:
            pytest_args.extend([f"-n={parallel}", "--dist=loadfile"])

        # Log pytest command
        logger.info(f"Running pytest with arguments: {pytest_args}")

        # Run pytest
        exit_code = pytest.main(pytest_args)

        # Calculate execution time
        execution_time = time.time() - self.start_time
        logger.info(
            f"Test execution completed in {execution_time:.2f} seconds with exit code: {exit_code}"
        )

        # Generate report if requested
        if report:
            self.generate_report()

        return exit_code

    @staticmethod
    def generate_report():
        """Generate test execution report."""
        logger.info("Generating Allure report")
        try:
            generate_allure_report()
            logger.info("Allure report generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate Allure report: {e}")

    def collect_metrics(self):
        """
        Collect and return execution metrics.

        Returns:
            dict: Execution metrics
        """
        # Calculate execution time
        execution_time = time.time() - self.start_time

        # Get test results from Allure results if available
        test_results = self._parse_test_results()

        metrics = {
            "execution_time": execution_time,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_results": test_results,
            "configuration": self.config,
        }

        logger.info(f"Collected metrics: {metrics}")
        return metrics

    @staticmethod
    def _parse_test_results():
        """
        Parse test results from Allure results.

        Returns:
            dict: Test results summary
        """
        try:
            # Count result files by type
            results_dir = Path("allure-results")
            if not results_dir.exists():
                return {"error": "No results directory found"}

            passed = len(list(results_dir.glob("*-passed.json")))
            failed = len(list(results_dir.glob("*-failed.json")))
            skipped = len(list(results_dir.glob("*-skipped.json")))
            broken = len(list(results_dir.glob("*-broken.json")))

            total = passed + failed + skipped + broken

            return {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "broken": broken,
                "pass_rate": (passed / total) * 100 if total > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error parsing test results: {e}")
            return {"error": str(e)}


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Test Automation Framework")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--tests", help="Path to test files or directories")
    parser.add_argument("--markers", help="Pytest markers to filter tests")
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel processes (0 = auto)",
    )
    parser.add_argument(
        "--no-report", action="store_true", help="Disable report generation"
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="Only collect tests without execution",
    )

    return parser.parse_args()


def main():
    """Initialize and run the test automation framework."""
    # Load configuration settings
    config = load_config()
    print("Configuration Loaded:", config)

    # Here you can call your test runner or setup your test environment
    print("Running Test Automation Framework...")
    # Ideally, invoke the tests (using pytest or custom logic)


if __name__ == "__main__":
    main()
