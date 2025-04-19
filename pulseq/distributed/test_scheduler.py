"""
Test scheduler implementation for distributed testing.

This module handles test distribution, load balancing, and scheduling.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .test_runner import DistributedTestRunner, TestNode


class TestScheduler:
    """Manages test scheduling and distribution."""

    def __init__(self, test_runner: DistributedTestRunner):
        """
        Initialize the test scheduler.

        Args:
            test_runner: DistributedTestRunner instance
        """
        self.test_runner = test_runner
        self.logger = logging.getLogger(__name__)
        self.scheduled_tests: Dict[str, Dict[str, Any]] = {}

    async def schedule_tests(self, tests: List[Dict[str, Any]]) -> None:
        """
        Schedule a batch of tests for execution.

        Args:
            tests: List of test cases to schedule
        """
        for test in tests:
            test_id = test["id"]
            self.scheduled_tests[test_id] = {
                "test": test,
                "status": "pending",
                "assigned_node": None,
                "start_time": None,
                "end_time": None,
            }

        self.logger.info(f"Scheduled {len(tests)} tests for execution")

    async def assign_tests(self) -> None:
        """Assign pending tests to available nodes."""
        available_nodes = self.test_runner.get_available_nodes()
        if not available_nodes:
            self.logger.warning("No available nodes for test assignment")
            return

        for test_id, test_info in self.scheduled_tests.items():
            if test_info["status"] == "pending":
                # Find the least loaded node
                node = self._find_least_loaded_node(available_nodes)
                if node:
                    await self._assign_test_to_node(test_id, node)

    def _find_least_loaded_node(self, nodes: Dict[str, TestNode]) -> Optional[TestNode]:
        """
        Find the node with the least load.

        Args:
            nodes: Dictionary of available nodes

        Returns:
            Least loaded TestNode instance, or None if no nodes available
        """
        if not nodes:
            return None

        # Count running tests per node
        node_load = {node_id: 0 for node_id in nodes}
        for test_info in self.scheduled_tests.values():
            if test_info["status"] == "running" and test_info["assigned_node"]:
                node_id = test_info["assigned_node"]
                if node_id in node_load:
                    node_load[node_id] += 1

        # Find node with minimum load
        min_load = min(node_load.values())
        for node_id, load in node_load.items():
            if load == min_load:
                return nodes[node_id]

        return None

    async def _assign_test_to_node(self, test_id: str, node: TestNode) -> None:
        """
        Assign a test to a specific node.

        Args:
            test_id: ID of the test to assign
            node: TestNode instance to assign the test to
        """
        test_info = self.scheduled_tests[test_id]
        test_info["status"] = "running"
        test_info["assigned_node"] = node.id
        test_info["start_time"] = datetime.now()

        self.logger.info(f"Assigned test {test_id} to node {node.id}")

        # Add test to node's queue
        await self.test_runner.distribute_tests([test_info["test"]])

    async def update_test_status(self, test_id: str, status: str) -> None:
        """
        Update the status of a test.

        Args:
            test_id: ID of the test to update
            status: New status for the test
        """
        if test_id in self.scheduled_tests:
            test_info = self.scheduled_tests[test_id]
            test_info["status"] = status
            if status in ["completed", "failed", "error"]:
                test_info["end_time"] = datetime.now()

            self.logger.info(f"Updated test {test_id} status to {status}")

    def get_test_status(self, test_id: str) -> Optional[str]:
        """
        Get the status of a test.

        Args:
            test_id: ID of the test to check

        Returns:
            Current status of the test, or None if test not found
        """
        return self.scheduled_tests.get(test_id, {}).get("status")

    def get_node_load(self, node_id: str) -> int:
        """
        Get the current load of a node.

        Args:
            node_id: ID of the node to check

        Returns:
            Number of tests currently running on the node
        """
        return sum(
            1
            for test_info in self.scheduled_tests.values()
            if test_info["status"] == "running"
            and test_info["assigned_node"] == node_id
        )

    def get_scheduled_tests(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all scheduled tests.

        Returns:
            Dictionary of scheduled tests
        """
        return self.scheduled_tests
