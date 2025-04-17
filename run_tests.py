# run_tests.py
import argparse
import logging
import os
import sys

import pytest

from framework.config import load_config
from framework.utilities.logger import setup_logger


def main():
    """Run tests with enhanced debugging and reporting."""
    parser = argparse.ArgumentParser(description="Run test automation framework tests")
    parser.add_argument(
        "--test-path", default="tests", help="Path to test files/directories"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Increase verbosity"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--allure", action="store_true", help="Generate Allure reports")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument(
        "--browser", default="chrome", help="Browser to use (chrome, firefox)"
    )
    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger("test_runner", level=log_level)

    # Set environment variables
    if args.browser:
        os.environ["TEST_BROWSER"] = args.browser

    # Load config
    config = load_config()
    logger.info(f"Running tests with configuration: {config}")

    # Build pytest args
    pytest_args = [args.test_path]

    if args.verbose:
        pytest_args.append("-v")

    if args.debug:
        pytest_args.append("--log-cli-level=DEBUG")

    if args.allure:
        pytest_args.append("--alluredir=allure-results")

    if args.parallel:
        pytest_args.extend(["-n", "auto"])

    # Add better test output
    pytest_args.extend(["-v", "--tb=native", "--showlocals"])

    logger.info(f"Running pytest with args: {pytest_args}")

    # Run tests
    result = pytest.main(pytest_args)

    # Generate Allure report if requested
    if args.allure:
        try:
            logger.info("Generating Allure report...")
            from framework.reporting import generate_allure_report

            generate_allure_report()
        except Exception as e:
            logger.error(f"Failed to generate Allure report: {e}")

    return result


if __name__ == "__main__":
    sys.exit(main())
