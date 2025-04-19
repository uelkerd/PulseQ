"""
Distributed test runner implementation.

This module provides the core functionality for running tests across multiple nodes.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class TestNode:
    """Represents a test execution node."""

    id: str
    host: str
    port: int
    status: str = "idle"
    last_heartbeat: Optional[datetime] = None
    capabilities: Dict[str, Any] = None


class DistributedTestRunner:
    """Manages distributed test execution across multiple nodes."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the distributed test runner.

        Args:
            config: Configuration dictionary containing node information
                   and test distribution settings
        """
        self.config = config
        self.nodes: Dict[str, TestNode] = {}
        self.logger = logging.getLogger(__name__)
        self.test_queue = asyncio.Queue()
        self.results_queue = asyncio.Queue()

    async def add_node(self, node: TestNode) -> None:
        """Add a new test node to the cluster."""
        self.nodes[node.id] = node
        self.logger.info(f"Added node {node.id} at {node.host}:{node.port}")

    async def remove_node(self, node_id: str) -> None:
        """Remove a node from the cluster."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.logger.info(f"Removed node {node_id}")

    async def distribute_tests(self, tests: List[Dict[str, Any]]) -> None:
        """
        Distribute tests across available nodes.

        Args:
            tests: List of test cases to distribute
        """
        for test in tests:
            await self.test_queue.put(test)
        self.logger.info(f"Distributed {len(tests)} tests to queue")

    async def run_tests(self) -> Dict[str, Any]:
        """
        Run the distributed test suite.

        Returns:
            Dictionary containing aggregated test results
        """
        tasks = []
        for node_id, node in self.nodes.items():
            if node.status == "idle":
                task = asyncio.create_task(self._run_node_tests(node))
                tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

        # Aggregate results
        results = await self._aggregate_results()
        return results

    async def _run_node_tests(self, node: TestNode) -> None:
        """Run tests on a specific node."""
        while not self.test_queue.empty():
            test = await self.test_queue.get()
            try:
                # Update node status
                node.status = "running"
                self.logger.info(f"Running test {test['id']} on node {node.id}")

                # Execute test (placeholder for actual test execution)
                result = await self._execute_test(node, test)

                # Queue result
                await self.results_queue.put(result)

            except Exception as e:
                self.logger.error(f"Error running test on node {node.id}: {str(e)}")
                await self.results_queue.put(
                    {"test_id": test["id"], "status": "error", "error": str(e)}
                )
            finally:
                node.status = "idle"
                self.test_queue.task_done()

    async def _execute_test(
        self, node: TestNode, test: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single test on a node."""
        # Placeholder for actual test execution
        # This would involve communicating with the node to run the test
        return {
            "test_id": test["id"],
            "node_id": node.id,
            "status": "passed",
            "duration": 1.0,
            "timestamp": datetime.now().isoformat(),
        }

    async def _aggregate_results(self) -> Dict[str, Any]:
        """Aggregate results from all nodes."""
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "duration": 0.0,
            "node_results": {},
        }

        while not self.results_queue.empty():
            result = await self.results_queue.get()
            results["total_tests"] += 1

            if result["status"] == "passed":
                results["passed"] += 1
            elif result["status"] == "failed":
                results["failed"] += 1
            else:
                results["errors"] += 1

            node_id = result["node_id"]
            if node_id not in results["node_results"]:
                results["node_results"][node_id] = []
            results["node_results"][node_id].append(result)

            results["duration"] += result.get("duration", 0.0)

        return results
