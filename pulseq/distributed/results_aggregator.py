"""
Results aggregator implementation for distributed testing.

This module handles test result collection, aggregation, and reporting.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class TestResult:
    """Represents a test execution result."""

    test_id: str
    node_id: str
    status: str
    duration: float
    timestamp: datetime
    error: str = None
    metrics: Dict[str, Any] = None


class ResultsAggregator:
    """Aggregates and manages test results."""

    def __init__(self):
        """Initialize the results aggregator."""
        self.results: Dict[str, TestResult] = {}
        self.logger = logging.getLogger(__name__)

    def add_result(self, result: TestResult) -> None:
        """
        Add a test result to the aggregator.

        Args:
            result: TestResult instance to add
        """
        self.results[result.test_id] = result
        self.logger.info(f"Added result for test {result.test_id}")

    def get_results(self) -> Dict[str, TestResult]:
        """
        Get all test results.

        Returns:
            Dictionary of test results
        """
        return self.results

    def get_test_result(self, test_id: str) -> Optional[TestResult]:
        """
        Get the result for a specific test.

        Args:
            test_id: ID of the test to get results for

        Returns:
            TestResult instance, or None if not found
        """
        return self.results.get(test_id)

    def get_node_results(self, node_id: str) -> List[TestResult]:
        """
        Get all results from a specific node.

        Args:
            node_id: ID of the node to get results for

        Returns:
            List of TestResult instances from the node
        """
        return [result for result in self.results.values() if result.node_id == node_id]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all test results.

        Returns:
            Dictionary containing test result summary
        """
        total_tests = len(self.results)
        passed = sum(1 for r in self.results.values() if r.status == "passed")
        failed = sum(1 for r in self.results.values() if r.status == "failed")
        errors = sum(1 for r in self.results.values() if r.status == "error")

        total_duration = sum(r.duration for r in self.results.values())
        avg_duration = total_duration / total_tests if total_tests > 0 else 0

        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "start_time": (
                min(r.timestamp for r in self.results.values())
                if self.results
                else None
            ),
            "end_time": (
                max(r.timestamp for r in self.results.values())
                if self.results
                else None
            ),
        }

    def get_node_summary(self, node_id: str) -> Dict[str, Any]:
        """
        Get a summary of results from a specific node.

        Args:
            node_id: ID of the node to get summary for

        Returns:
            Dictionary containing node result summary
        """
        node_results = self.get_node_results(node_id)
        if not node_results:
            return {}

        total_tests = len(node_results)
        passed = sum(1 for r in node_results if r.status == "passed")
        failed = sum(1 for r in node_results if r.status == "failed")
        errors = sum(1 for r in node_results if r.status == "error")

        total_duration = sum(r.duration for r in node_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0

        return {
            "node_id": node_id,
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "start_time": min(r.timestamp for r in node_results),
            "end_time": max(r.timestamp for r in node_results),
        }

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all test metrics.

        Returns:
            Dictionary containing metrics summary
        """
        metrics_summary = {}

        for result in self.results.values():
            if result.metrics:
                for metric_name, value in result.metrics.items():
                    if metric_name not in metrics_summary:
                        metrics_summary[metric_name] = {
                            "values": [],
                            "min": float("inf"),
                            "max": float("-inf"),
                            "sum": 0,
                        }

                    metrics_summary[metric_name]["values"].append(value)
                    metrics_summary[metric_name]["min"] = min(
                        metrics_summary[metric_name]["min"], value
                    )
                    metrics_summary[metric_name]["max"] = max(
                        metrics_summary[metric_name]["max"], value
                    )
                    metrics_summary[metric_name]["sum"] += value

        # Calculate averages
        for metric in metrics_summary.values():
            if metric["values"]:
                metric["avg"] = metric["sum"] / len(metric["values"])

        return metrics_summary
