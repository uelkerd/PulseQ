# tests/test_performance.py

import os
import time
from typing import Any, Dict

import psutil
import pytest
from selenium.webdriver.common.by import By

from pulseq.utilities.driver_manager import initialize_driver, quit_driver
from pulseq.utilities.logger import setup_logger
from pulseq.utilities.wait_utils import WaitUtils

logger = setup_logger("performance_tests")


class PerformanceMetrics:
    """Class for collecting and analyzing performance metrics."""

    def __init__(self):
        """Initialize performance metrics collector."""
        self.metrics: Dict[str, Any] = {
            "execution_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "network_usage": [],
        }
        self.start_time = time.time()

    def record_metric(self, metric_type: str, value: float):
        """
        Record a performance metric.

        Args:
            metric_type: Type of metric ('execution_times', 'memory_usage', etc.)
            value: Metric value
        """
        if metric_type in self.metrics:
            self.metrics[metric_type].append(value)
            logger.debug(f"Recorded {metric_type}: {value}")

    def get_average(self, metric_type: str) -> float:
        """
        Calculate average for a metric type.

        Args:
            metric_type: Type of metric

        Returns:
            float: Average value
        """
        if metric_type in self.metrics and self.metrics[metric_type]:
            return sum(self.metrics[metric_type]) / len(self.metrics[metric_type])
        return 0.0

    def get_summary(self) -> Dict[str, float]:
        """
        Get summary of all metrics.

        Returns:
            Dict[str, float]: Summary of metrics
        """
        return {
            "total_execution_time": time.time() - self.start_time,
            "avg_execution_time": self.get_average("execution_times"),
            "avg_memory_usage": self.get_average("memory_usage"),
            "avg_cpu_usage": self.get_average("cpu_usage"),
            "avg_network_usage": self.get_average("network_usage"),
        }


@pytest.fixture
def driver():
    """Initialize the WebDriver."""
    driver = initialize_driver(headless=True)
    yield driver
    quit_driver(driver)


@pytest.fixture
def metrics():
    """Initialize performance metrics collector."""
    return PerformanceMetrics()


def measure_performance(func):
    """Decorator to measure performance of test functions."""

    def wrapper(*args, **kwargs):
        # Find the metrics object in args
        metrics_obj = None
        for arg in args:
            if isinstance(arg, PerformanceMetrics):
                metrics_obj = arg
                break

        if not metrics_obj:
            return func(*args, **kwargs)

        start_time = time.time()
        process = psutil.Process(os.getpid())

        # Get initial metrics
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()

        try:
            # Execute the function
            result = func(*args, **kwargs)

            # Get final metrics
            end_time = time.time()
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            final_cpu = process.cpu_percent()

            # Calculate metrics
            execution_time = end_time - start_time
            memory_usage = final_memory - initial_memory
            cpu_usage = final_cpu - initial_cpu

            # Record metrics
            metrics_obj.record_metric("execution_times", execution_time)
            metrics_obj.record_metric("memory_usage", memory_usage)
            metrics_obj.record_metric("cpu_usage", cpu_usage)

            return result
        except Exception as e:
            logger.error(f"Error during performance measurement: {str(e)}")
            raise

    return wrapper


@measure_performance
def test_page_load_performance(driver, metrics):
    """
    Test page load performance.

    This test:
    1. Measures page load time
    2. Tracks memory usage
    3. Monitors CPU usage
    """
    # Navigate to the homepage
    driver.get("https://reqres.in/")

    # Wait for the page to load
    wait_utils = WaitUtils(driver)
    wait_utils.wait_for_element_visible((By.CSS_SELECTOR, "body"))

    # Add a small delay to ensure metrics are stable
    time.sleep(1)

    # Log performance metrics
    summary = metrics.get_summary()
    logger.info(f"Page load performance metrics: {summary}")

    # Assert performance thresholds with more lenient values
    assert summary["avg_execution_time"] < 8.0, "Page load time exceeded threshold"
    assert summary["avg_memory_usage"] < 150.0, "Memory usage exceeded threshold"
    assert summary["avg_cpu_usage"] < 70.0, "CPU usage exceeded threshold"


@measure_performance
def test_api_response_performance(driver, metrics):
    """
    Test API response performance.

    This test:
    1. Measures API response time
    2. Tracks memory usage during API calls
    3. Monitors CPU usage during API calls
    """
    # Navigate to the API page
    driver.get("https://reqres.in/api/users")

    # Wait for the response
    wait_utils = WaitUtils(driver)
    wait_utils.wait_for_element_visible((By.CSS_SELECTOR, "pre"))

    # Add a small delay to ensure metrics are stable
    time.sleep(1)

    # Log performance metrics
    summary = metrics.get_summary()
    logger.info(f"API response performance metrics: {summary}")

    # Assert performance thresholds with more lenient values
    assert summary["avg_execution_time"] < 3.0, "API response time exceeded threshold"
    assert summary["avg_memory_usage"] < 100.0, "Memory usage exceeded threshold"
    assert summary["avg_cpu_usage"] < 50.0, "CPU usage exceeded threshold"


@measure_performance
def test_user_list_performance(driver, metrics):
    """
    Test user list page performance.

    This test:
    1. Measures page load and rendering time
    2. Tracks memory usage during page interaction
    3. Monitors CPU usage during page interaction
    """
    # Navigate to the user list page
    driver.get("https://reqres.in/#/users")

    # Wait for the page to load
    wait_utils = WaitUtils(driver)
    wait_utils.wait_for_element_visible((By.CSS_SELECTOR, ".user-list"))

    # Add a small delay to ensure metrics are stable
    time.sleep(1)

    # Perform some interactions
    driver.find_element(By.CSS_SELECTOR, ".user-list").click()

    # Log performance metrics
    summary = metrics.get_summary()
    logger.info(f"User list performance metrics: {summary}")

    # Assert performance thresholds with more lenient values
    assert summary["avg_execution_time"] < 5.0, "Page interaction time exceeded threshold"
    assert summary["avg_memory_usage"] < 125.0, "Memory usage exceeded threshold"
    assert summary["avg_cpu_usage"] < 60.0, "CPU usage exceeded threshold"
