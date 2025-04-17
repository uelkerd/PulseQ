# pulseq/utilities/performance_metrics.py

import functools
import json
import os
import platform
import statistics
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Dict, List, Optional

import psutil

from pulseq.utilities.logger import setup_logger

# Set up module logger
logger = setup_logger("performance_metrics")


class PerformanceMetrics:
    """
    Class for collecting, analyzing, and reporting performance metrics for test execution.
    Supports tracking execution times, resource usage, and historical performance trends.
    """

    def __init__(self, metrics_file="metrics/performance_history.json"):
        """
        Initialize the performance metrics handler.

        Args:
            metrics_file: Path to the metrics history file
        """
        self.metrics_file = metrics_file
        self.current_metrics = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": self._get_system_info(),
            "tests": {},
            "execution_summary": {
                "start_time": time.time(),
                "total_duration": 0,
                "tests_executed": 0,
                "tests_passed": 0,
                "tests_failed": 0,
            },
        }

        # Ensure metrics directory exists
        metrics_dir = os.path.dirname(metrics_file)
        Path(metrics_dir).mkdir(parents=True, exist_ok=True)

        logger.debug(
            f"Initialized performance metrics handler with file: {metrics_file}"
        )

    @staticmethod
    def _get_system_info():
        """
        Get system information for context.

        Returns:
            dict: System information
        """
        try:
            return {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "processor": platform.processor(),
                "cpu_count": os.cpu_count(),
                "memory_total": psutil.virtual_memory().total
                / (1024 * 1024 * 1024),  # GB
                "hostname": platform.node(),
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": "Failed to get system info"}

    @staticmethod
    def get_resource_usage():
        """
        Get current resource usage.

        Returns:
            dict: Resource usage metrics
        """
        try:
            process = psutil.Process(os.getpid())
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_usage": process.memory_info().rss / (1024 * 1024),  # MB
                "memory_percent": process.memory_percent(),
                "thread_count": process.num_threads(),
                "open_files": len(process.open_files()),
                "total_cpu_percent": psutil.cpu_percent(),
                "total_memory_percent": psutil.virtual_memory().percent,
            }
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {"error": "Failed to get resource usage"}

    def start_test_timer(self, test_name):
        """
        Start timing a test.

        Args:
            test_name: Name of the test

        Returns:
            float: Start time
        """
        start_time = time.time()

        if test_name not in self.current_metrics["tests"]:
            self.current_metrics["tests"][test_name] = {
                "start_time": start_time,
                "end_time": None,
                "duration": None,
                "result": None,
                "resource_usage_start": self.get_resource_usage(),
            }

        logger.debug(f"Started timer for test: {test_name}")
        return start_time

    def stop_test_timer(self, test_name, result=True):
        """
        Stop timing a test and record the result.

        Args:
            test_name: Name of the test
            result: Test result (True = passed, False = failed)

        Returns:
            float: Test duration in seconds
        """
        end_time = time.time()

        if test_name in self.current_metrics["tests"]:
            test_data = self.current_metrics["tests"][test_name]
            test_data["end_time"] = end_time
            test_data["result"] = result

            # Calculate duration
            if test_data["start_time"]:
                test_data["duration"] = end_time - test_data["start_time"]

            # Record end resource usage
            test_data["resource_usage_end"] = self.get_resource_usage()

            # Update summary
            self.current_metrics["execution_summary"]["tests_executed"] += 1
            if result:
                self.current_metrics["execution_summary"]["tests_passed"] += 1
            else:
                self.current_metrics["execution_summary"]["tests_failed"] += 1

            logger.debug(
                f"Stopped timer for test: {test_name}, duration: {test_data['duration']:.2f}s, result: {result}"
            )

            return test_data["duration"]
        logger.warning(f"No timer started for test: {test_name}")
        return None

    def finalize_metrics(self):
        """
        Finalize metrics after all tests are executed.

        Returns:
            dict: Finalized metrics
        """
        # Calculate total duration
        end_time = time.time()
        self.current_metrics["execution_summary"]["end_time"] = end_time
        self.current_metrics["execution_summary"]["total_duration"] = (
            end_time - self.current_metrics["execution_summary"]["start_time"]
        )

        # Add final resource usage
        self.current_metrics["execution_summary"]["final_resource_usage"] = (
            self.get_resource_usage()
        )

        # Calculate statistics
        durations = [
            test_data["duration"]
            for test_data in self.current_metrics["tests"].values()
            if test_data["duration"] is not None
        ]

        if durations:
            self.current_metrics["execution_summary"]["statistics"] = {
                "min_duration": min(durations),
                "max_duration": max(durations),
                "avg_duration": statistics.mean(durations),
                "median_duration": statistics.median(durations),
                "total_test_time": sum(durations),
            }

        logger.info(
            f"Finalized metrics: {len(self.current_metrics['tests'])} tests, "
            f"total duration: {self.current_metrics['execution_summary']['total_duration']:.2f}s"
        )

        return self.current_metrics

    def save_metrics(self):
        """
        Save current metrics to the history file.

        Returns:
            bool: True if saved successfully
        """
        try:
            # Ensure we have finalized metrics
            if "end_time" not in self.current_metrics["execution_summary"]:
                self.finalize_metrics()

            # Load existing history if available
            history = []
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, "r") as f:
                    try:
                        history = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning(
                            f"Invalid JSON in metrics file: {self.metrics_file}, starting new history"
                        )
                        history = []

            # Append current metrics and save
            history.append(self.current_metrics)

            with open(self.metrics_file, "w") as f:
                json.dump(history, f, indent=2)

            logger.info(f"Saved metrics to: {self.metrics_file}")
            return True

        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            return False

    def compare_with_history(self, limit=5):
        """
        Compare current metrics with historical data.

        Args:
            limit: Number of previous runs to compare with

        Returns:
            dict: Comparison results
        """
        try:
            # Ensure we have current metrics
            if "end_time" not in self.current_metrics["execution_summary"]:
                self.finalize_metrics()

            # Load history
            if not os.path.exists(self.metrics_file):
                return {"error": "No history file found for comparison"}

            with open(self.metrics_file, "r") as f:
                history = json.load(f)

            # Get the last N runs (excluding current run)
            previous_runs = history[-limit - 1 : -1] if len(history) > 1 else []

            if not previous_runs:
                return {"warning": "No previous runs found for comparison"}

            # Calculate averages from previous runs
            prev_durations = [
                run["execution_summary"]["total_duration"] for run in previous_runs
            ]
            prev_avg_duration = statistics.mean(prev_durations)

            current_duration = self.current_metrics["execution_summary"][
                "total_duration"
            ]

            # Calculate improvement
            improvement = {
                "previous_avg_duration": prev_avg_duration,
                "current_duration": current_duration,
                "absolute_diff": prev_avg_duration - current_duration,
                "percent_diff": (
                    (prev_avg_duration - current_duration) / prev_avg_duration
                )
                * 100,
            }

            # Compare individual tests if they exist in both current and previous
            test_comparisons = {}
            for test_name, test_data in self.current_metrics["tests"].items():
                # Find the same test in previous runs
                prev_test_data = [
                    run["tests"].get(test_name)
                    for run in previous_runs
                    if test_name in run["tests"]
                ]

                if prev_test_data:
                    prev_durations = [
                        d["duration"]
                        for d in prev_test_data
                        if d["duration"] is not None
                    ]
                    if prev_durations:
                        prev_avg = statistics.mean(prev_durations)
                        test_comparisons[test_name] = {
                            "previous_avg": prev_avg,
                            "current": test_data["duration"],
                            "absolute_diff": prev_avg - test_data["duration"],
                            "percent_diff": (
                                (prev_avg - test_data["duration"]) / prev_avg
                            )
                            * 100,
                        }

            result = {
                "overall_improvement": improvement,
                "test_comparisons": test_comparisons,
                "compared_runs": len(previous_runs),
            }

            logger.info(
                f"Comparison with history: {result['overall_improvement']['percent_diff']:.2f}% "
                f"difference from previous average"
            )

            return result

        except Exception as e:
            logger.error(f"Error comparing with history: {e}")
            return {"error": str(e)}

    def generate_report(self, output_file="metrics/performance_report.json"):
        """
        Generate a comprehensive performance report.

        Args:
            output_file: Path to save the report

        Returns:
            dict: Report data
        """
        try:
            # Ensure directories exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Finalize metrics
            if "end_time" not in self.current_metrics["execution_summary"]:
                self.finalize_metrics()

            # Get historical comparison
            comparison = self.compare_with_history()

            # Generate report
            report = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "current_metrics": self.current_metrics,
                "historical_comparison": comparison,
                "summary": {
                    "total_tests": self.current_metrics["execution_summary"][
                        "tests_executed"
                    ],
                    "pass_rate": (
                        (
                            self.current_metrics["execution_summary"]["tests_passed"]
                            / self.current_metrics["execution_summary"][
                                "tests_executed"
                            ]
                            * 100
                        )
                        if self.current_metrics["execution_summary"]["tests_executed"]
                        > 0
                        else 0
                    ),
                    "total_duration": self.current_metrics["execution_summary"][
                        "total_duration"
                    ],
                    "improvement": comparison.get("overall_improvement", {}).get(
                        "percent_diff", 0
                    ),
                },
            }

            # Save report
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"Generated performance report: {output_file}")
            return report

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {"error": str(e)}


# Decorator for timing tests
def measure_performance(metrics_instance=None):
    """
    Decorator to measure performance of a test function.

    Args:
        metrics_instance: Instance of PerformanceMetrics (if None, a new one is created)

    Returns:
        function: Decorated function
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create metrics instance
            nonlocal metrics_instance
            if metrics_instance is None:
                metrics_instance = PerformanceMetrics()

            # Start timer
            test_name = func.__name__
            metrics_instance.start_test_timer(test_name)

            # Run the test
            try:
                result = func(*args, **kwargs)
                # Stop timer with success
                metrics_instance.stop_test_timer(test_name, result=True)
                return result
            except Exception as e:
                # Stop timer with failure
                metrics_instance.stop_test_timer(test_name, result=False)
                raise

        return wrapper

    return decorator


# Example usage
if __name__ == "__main__":
    # Create metrics instance
    metrics = PerformanceMetrics()

    # Example test functions
    @measure_performance(metrics)
    def test_example_1():
        time.sleep(0.5)
        return True

    @measure_performance(metrics)
    def test_example_2():
        time.sleep(1)
        return True

    # Run tests
    test_example_1()
    test_example_2()

    # Finalize and save metrics
    metrics.finalize_metrics()
    metrics.save_metrics()

    # Generate report
    report = metrics.generate_report()
    print(f"Report summary: {report['summary']}")
