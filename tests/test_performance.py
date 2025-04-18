# tests/test_performance.py

import os
import time
from typing import Any, Dict

import psutil
import pytest
from selenium.webdriver.common.by import By

from pulseq.utilities.logger import setup_logger
from pulseq.utilities.performance_metrics import PerformanceMetrics
from pulseq.utilities.wait_utils import WaitUtils

logger = setup_logger("performance_tests")


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


def test_page_load_performance(driver, metrics):
    """
    Test page load performance with browser caching and detailed timing metrics.
    """
    metrics.start_test_timer("page_load")

    # Enable browser caching
    driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": False})

    # First load - cold start
    driver.get("https://reqres.in/")
    wait_utils = WaitUtils(driver)
    wait_utils.wait_for_element_visible((By.CSS_SELECTOR, "body"))

    # Get detailed timing metrics
    timing_metrics = driver.execute_script("""
        let t = window.performance.timing;
        let timing = {};
        timing.dns = t.domainLookupEnd - t.domainLookupStart;
        timing.tcp = t.connectEnd - t.connectStart;
        timing.ttfb = t.responseStart - t.navigationStart;
        timing.download = t.responseEnd - t.responseStart;
        timing.dom_load = t.domComplete - t.domLoading;
        timing.total = t.loadEventEnd - t.navigationStart;
        return timing;
    """)

    # Log detailed timing metrics
    logger.info("Page Load Timing Breakdown:")
    for metric, value in timing_metrics.items():
        logger.info(f"{metric}: {value/1000:.2f}s")

    # Measure cached load
    driver.refresh()
    cached_load_time = driver.execute_script("""
        let t = window.performance.timing;
        return t.loadEventEnd - t.navigationStart;
    """)

    # Get resource usage
    resource_usage = metrics.get_resource_usage()
    logger.info(f"Page load resource usage: {resource_usage}")

    # Stop timer and get duration
    duration = metrics.stop_test_timer("page_load")
    logger.info(f"Initial page load: {timing_metrics['total']/1000:.2f}s")
    logger.info(f"Cached page load: {cached_load_time/1000:.2f}s")

    # Assert performance thresholds with separate cached metrics
    assert (
        timing_metrics["total"] / 1000 < 10.0
    ), f"Initial page load time ({timing_metrics['total']/1000:.2f}s) exceeded threshold"
    assert (
        cached_load_time / 1000 < 5.0
    ), f"Cached page load time ({cached_load_time/1000:.2f}s) exceeded threshold"
    assert (
        resource_usage["memory_usage"] < 200.0
    ), f"Memory usage ({resource_usage['memory_usage']:.1f}MB) exceeded threshold"
    assert (
        resource_usage["cpu_percent"] < 80.0
    ), f"CPU usage ({resource_usage['cpu_percent']:.1f}%) exceeded threshold"

    # Assert specific timing thresholds
    assert (
        timing_metrics["ttfb"] / 1000 < 2.0
    ), f"Time to First Byte ({timing_metrics['ttfb']/1000:.2f}s) too high"
    assert (
        timing_metrics["dom_load"] / 1000 < 3.0
    ), f"DOM Load ({timing_metrics['dom_load']/1000:.2f}s) too high"


def test_api_response_performance(driver, metrics):
    """
    Test API response performance with connection pooling and concurrent requests.
    """
    metrics.start_test_timer("api_response")

    # Enable keep-alive connections
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd(
        "Network.setExtraHTTPHeaders", {"headers": {"Connection": "keep-alive"}}
    )

    # Test sequential API calls
    endpoints = [
        "https://reqres.in/api/users",
        "https://reqres.in/api/users?page=2",
        "https://reqres.in/api/users/2",
    ]

    response_times = []
    for endpoint in endpoints:
        start_time = time.time()
        driver.get(endpoint)
        wait_utils = WaitUtils(driver)
        wait_utils.wait_for_element_visible((By.CSS_SELECTOR, "pre"))
        response_time = time.time() - start_time
        response_times.append(response_time)
        logger.info(f"Response time for {endpoint}: {response_time:.2f}s")

    # Calculate statistics
    avg_response_time = sum(response_times) / len(response_times)
    max_response_time = max(response_times)

    # Get resource usage
    resource_usage = metrics.get_resource_usage()
    logger.info(f"API response resource usage: {resource_usage}")

    # Stop timer and get duration
    duration = metrics.stop_test_timer("api_response")
    logger.info(f"Average response time: {avg_response_time:.2f}s")
    logger.info(f"Maximum response time: {max_response_time:.2f}s")

    # Assert performance thresholds
    assert (
        avg_response_time < 1.5
    ), f"Average response time ({avg_response_time:.2f}s) exceeded threshold"
    assert (
        max_response_time < 2.0
    ), f"Maximum response time ({max_response_time:.2f}s) exceeded threshold"
    assert (
        resource_usage["memory_usage"] < 100.0
    ), f"Memory usage ({resource_usage['memory_usage']:.1f}MB) exceeded threshold"
    assert (
        resource_usage["cpu_percent"] < 50.0
    ), f"CPU usage ({resource_usage['cpu_percent']:.1f}%) exceeded threshold"


def test_user_list_performance(driver, metrics):
    """
    Test user list page performance with detailed rendering metrics.
    """
    metrics.start_test_timer("user_list")

    # Enable performance monitoring
    driver.execute_cdp_cmd("Performance.enable", {})

    # Navigate to the user list page
    driver.get("https://reqres.in/api/users?page=2")

    # Wait for the response and measure JSON parse time
    wait_utils = WaitUtils(driver)
    start_parse = time.time()
    wait_utils.wait_for_element_visible((By.CSS_SELECTOR, "pre"))

    # Get JSON content and measure parse time
    json_content = driver.execute_script(
        "return document.querySelector('pre').textContent"
    )
    parsed_data = driver.execute_script("return JSON.parse(arguments[0])", json_content)
    parse_time = time.time() - start_parse

    # Measure memory before and after data processing
    initial_memory = driver.execute_script(
        "return window.performance.memory.usedJSHeapSize"
    )

    # Simulate data processing
    driver.execute_script(
        """
        const data = arguments[0];
        // Process each user
        data.data.forEach(user => {
            const div = document.createElement('div');
            div.textContent = `${user.first_name} ${user.last_name}`;
            document.body.appendChild(div);
        });
    """,
        parsed_data,
    )

    final_memory = driver.execute_script(
        "return window.performance.memory.usedJSHeapSize"
    )
    memory_delta = (final_memory - initial_memory) / (1024 * 1024)  # Convert to MB

    # Get performance metrics
    perf_metrics = driver.execute_script("""
        const perf = window.performance;
        const timing = perf.timing;
        return {
            network: timing.responseEnd - timing.requestStart,
            processing: timing.domComplete - timing.responseEnd,
            memory_used: window.performance.memory.usedJSHeapSize / (1024 * 1024)
        }
    """)

    # Get resource usage
    resource_usage = metrics.get_resource_usage()

    # Log detailed metrics
    logger.info(f"Network time: {perf_metrics['network']/1000:.2f}s")
    logger.info(f"Processing time: {perf_metrics['processing']/1000:.2f}s")
    logger.info(f"JSON parse time: {parse_time:.2f}s")
    logger.info(f"Memory impact: {memory_delta:.2f}MB")
    logger.info(f"Total JS Heap: {perf_metrics['memory_used']:.2f}MB")

    # Stop timer and get duration
    duration = metrics.stop_test_timer("user_list")
    logger.info(f"Total duration: {duration:.2f}s")

    # Assert performance thresholds
    assert duration < 5.0, f"Total duration ({duration:.2f}s) exceeded threshold"
    assert parse_time < 0.5, f"JSON parse time ({parse_time:.2f}s) too high"
    assert memory_delta < 50.0, f"Memory impact ({memory_delta:.2f}MB) too high"
    assert (
        resource_usage["memory_usage"] < 120.0
    ), f"Memory usage ({resource_usage['memory_usage']:.1f}MB) exceeded threshold"
    assert (
        resource_usage["cpu_percent"] < 60.0
    ), f"CPU usage ({resource_usage['cpu_percent']:.1f}%) exceeded threshold"
