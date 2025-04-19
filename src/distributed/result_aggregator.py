import logging
import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .task_distributor import TestTask

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Represents a test execution result."""

    test_id: str
    node_id: str
    status: str
    duration: float
    timestamp: datetime
    error: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class ResultAggregator:
    """Aggregates and analyzes test results from distributed workers."""

    def __init__(self):
        self.results: Dict[str, List[TestResult]] = {}
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = {}
        self._aggregation_lock = asyncio.Lock()

    async def add_result(self, result: TestResult) -> None:
        """Add a new test result."""
        async with self._aggregation_lock:
            if result.test_id not in self.results:
                self.results[result.test_id] = []
            self.results[result.test_id].append(result)

            if result.metrics:
                if result.test_id not in self.metrics_history:
                    self.metrics_history[result.test_id] = []
                self.metrics_history[result.test_id].append(result.metrics)

            logger.info(
                f"Added result for test {result.test_id} from node {result.node_id}"
            )

    def get_test_summary(self, test_id: str) -> Dict[str, Any]:
        """Get summary statistics for a specific test."""
        if test_id not in self.results:
            return {"error": f"No results found for test {test_id}"}

        results = self.results[test_id]
        durations = [r.duration for r in results]
        statuses = [r.status for r in results]

        summary = {
            "test_id": test_id,
            "total_runs": len(results),
            "pass_count": statuses.count("passed"),
            "fail_count": statuses.count("failed"),
            "error_count": statuses.count("error"),
            "avg_duration": statistics.mean(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "std_dev": statistics.stdev(durations) if len(durations) > 1 else 0,
            "last_run": (
                max(r.timestamp for r in results).isoformat() if results else None
            ),
        }

        if test_id in self.metrics_history:
            metrics = self.metrics_history[test_id]
            if metrics:
                summary["metrics"] = self._aggregate_metrics(metrics)

        return summary

    def get_overall_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all tests."""
        all_results = [r for results in self.results.values() for r in results]
        all_durations = [r.duration for r in all_results]
        all_statuses = [r.status for r in all_results]

        summary = {
            "total_tests": len(self.results),
            "total_runs": len(all_results),
            "pass_count": all_statuses.count("passed"),
            "fail_count": all_statuses.count("failed"),
            "error_count": all_statuses.count("error"),
            "avg_duration": statistics.mean(all_durations) if all_durations else 0,
            "min_duration": min(all_durations) if all_durations else 0,
            "max_duration": max(all_durations) if all_durations else 0,
            "std_dev": statistics.stdev(all_durations) if len(all_durations) > 1 else 0,
            "last_run": (
                max(r.timestamp for r in all_results).isoformat()
                if all_results
                else None
            ),
        }

        return summary

    def _aggregate_metrics(self, metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate metrics from multiple runs."""
        if not metrics_list:
            return {}

        aggregated = {}
        for metric_name in metrics_list[0].keys():
            values = [m[metric_name] for m in metrics_list if metric_name in m]
            if values:
                aggregated[metric_name] = {
                    "avg": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                }

        return aggregated

    def get_failed_tests(self) -> List[Dict[str, Any]]:
        """Get details of all failed tests."""
        failed = []
        for test_id, results in self.results.items():
            failed_results = [r for r in results if r.status in ["failed", "error"]]
            if failed_results:
                failed.append(
                    {
                        "test_id": test_id,
                        "failures": len(failed_results),
                        "last_failure": max(
                            r.timestamp for r in failed_results
                        ).isoformat(),
                        "errors": [r.error for r in failed_results if r.error],
                    }
                )
        return failed

    def get_slow_tests(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """Get tests that exceed the duration threshold."""
        slow = []
        for test_id, results in self.results.items():
            avg_duration = statistics.mean(r.duration for r in results)
            if avg_duration > threshold:
                slow.append(
                    {
                        "test_id": test_id,
                        "avg_duration": avg_duration,
                        "runs": len(results),
                        "last_run": max(r.timestamp for r in results).isoformat(),
                    }
                )
        return sorted(slow, key=lambda x: x["avg_duration"], reverse=True)

    def get_node_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics per node."""
        node_stats = {}
        for results in self.results.values():
            for result in results:
                if result.node_id not in node_stats:
                    node_stats[result.node_id] = {
                        "total_tests": 0,
                        "passed": 0,
                        "failed": 0,
                        "errors": 0,
                        "durations": [],
                    }

                stats = node_stats[result.node_id]
                stats["total_tests"] += 1
                if result.status == "passed":
                    stats["passed"] += 1
                elif result.status == "failed":
                    stats["failed"] += 1
                else:
                    stats["errors"] += 1
                stats["durations"].append(result.duration)

        # Calculate averages
        for node_id, stats in node_stats.items():
            stats["avg_duration"] = (
                statistics.mean(stats["durations"]) if stats["durations"] else 0
            )
            stats["success_rate"] = (
                (stats["passed"] / stats["total_tests"]) * 100
                if stats["total_tests"]
                else 0
            )
            del stats["durations"]

        return node_stats
