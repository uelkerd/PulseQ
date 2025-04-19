"""
End-to-end integration tests for PulseQ framework.
"""

import asyncio
from datetime import datetime

import pytest

from pulseq.distributed import (
    DistributedTestRunner,
    NodeManager,
    ResultsAggregator,
    TestNode,
    TestScheduler,
)


@pytest.fixture
async def test_environment():
    """Set up test environment with multiple nodes."""
    runner = DistributedTestRunner()
    manager = NodeManager()
    scheduler = TestScheduler()
    aggregator = ResultsAggregator()

    # Create test nodes
    nodes = [
        TestNode(
            id=f"node{i}",
            host="localhost",
            port=8000 + i,
            capabilities={"os": "linux", "browser": "chrome", "memory": "8GB"},
        )
        for i in range(3)
    ]

    # Register nodes
    for node in nodes:
        await runner.add_node(node)
        await manager.register_node(node)

    # Start monitoring
    await manager.start_monitoring()

    yield {
        "runner": runner,
        "manager": manager,
        "scheduler": scheduler,
        "aggregator": aggregator,
        "nodes": nodes,
    }

    # Cleanup
    for node in nodes:
        await runner.remove_node(node.id)


@pytest.mark.asyncio
async def test_api_test_execution(test_environment):
    """Test API test execution in distributed environment."""
    runner = test_environment["runner"]
    scheduler = test_environment["scheduler"]

    # Define API tests
    api_tests = [
        {
            "id": f"api_test_{i}",
            "name": "test_api_endpoint",
            "type": "api",
            "priority": "high",
            "endpoint": "/api/users",
            "method": "GET",
            "expected_status": 200,
        }
        for i in range(10)
    ]

    # Schedule tests
    for test in api_tests:
        await scheduler.schedule_test(test)

    # Run tests
    results = await runner.run_tests()

    # Verify results
    assert len(results) == len(api_tests)
    assert all(result.status == "passed" for result in results)


@pytest.mark.asyncio
async def test_ui_test_execution(test_environment):
    """Test UI test execution in distributed environment."""
    runner = test_environment["runner"]
    scheduler = test_environment["scheduler"]

    # Define UI tests
    ui_tests = [
        {
            "id": f"ui_test_{i}",
            "name": "test_ui_element",
            "type": "ui",
            "priority": "medium",
            "url": "https://example.com",
            "element": "login_button",
            "action": "click",
        }
        for i in range(5)
    ]

    # Schedule tests
    for test in ui_tests:
        await scheduler.schedule_test(test)

    # Run tests
    results = await runner.run_tests()

    # Verify results
    assert len(results) == len(ui_tests)
    assert all(result.status == "passed" for result in results)


@pytest.mark.asyncio
async def test_performance_test_execution(test_environment):
    """Test performance test execution in distributed environment."""
    runner = test_environment["runner"]
    scheduler = test_environment["scheduler"]

    # Define performance tests
    perf_tests = [
        {
            "id": f"perf_test_{i}",
            "name": "test_load_time",
            "type": "performance",
            "priority": "high",
            "url": "https://example.com",
            "concurrent_users": 100,
            "duration": 60,
            "metrics": ["response_time", "throughput"],
        }
        for i in range(3)
    ]

    # Schedule tests
    for test in perf_tests:
        await scheduler.schedule_test(test)

    # Run tests
    results = await runner.run_tests()

    # Verify results
    assert len(results) == len(perf_tests)
    assert all(result.status == "passed" for result in results)
    assert all("metrics" in result.__dict__ for result in results)


@pytest.mark.asyncio
async def test_mixed_test_execution(test_environment):
    """Test execution of mixed test types in distributed environment."""
    runner = test_environment["runner"]
    scheduler = test_environment["scheduler"]

    # Define mixed tests
    mixed_tests = (
        [
            # API tests
            {
                "id": f"api_test_{i}",
                "name": "test_api",
                "type": "api",
                "priority": "high",
            }
            for i in range(5)
        ]
        + [
            # UI tests
            {
                "id": f"ui_test_{i}",
                "name": "test_ui",
                "type": "ui",
                "priority": "medium",
            }
            for i in range(5)
        ]
        + [
            # Performance tests
            {
                "id": f"perf_test_{i}",
                "name": "test_perf",
                "type": "performance",
                "priority": "low",
            }
            for i in range(5)
        ]
    )

    # Schedule tests
    for test in mixed_tests:
        await scheduler.schedule_test(test)

    # Run tests
    results = await runner.run_tests()

    # Verify results
    assert len(results) == len(mixed_tests)
    assert all(result.status == "passed" for result in results)


@pytest.mark.asyncio
async def test_node_failure_handling(test_environment):
    """Test handling of node failures during test execution."""
    runner = test_environment["runner"]
    scheduler = test_environment["scheduler"]
    manager = test_environment["manager"]

    # Define tests
    tests = [
        {"id": f"test_{i}", "name": "test_endpoint", "type": "api", "priority": "high"}
        for i in range(10)
    ]

    # Schedule tests
    for test in tests:
        await scheduler.schedule_test(test)

    # Simulate node failure
    await runner.remove_node(test_environment["nodes"][0].id)

    # Run tests
    results = await runner.run_tests()

    # Verify results
    assert len(results) == len(tests)
    assert all(result.status == "passed" for result in results)


@pytest.mark.asyncio
async def test_load_balancing(test_environment):
    """Test load balancing across nodes."""
    runner = test_environment["runner"]
    scheduler = test_environment["scheduler"]

    # Define large number of tests
    tests = [
        {
            "id": f"test_{i}",
            "name": "test_endpoint",
            "type": "api",
            "priority": "high",
            "duration": 1.0,
        }
        for i in range(100)
    ]

    # Schedule tests
    for test in tests:
        await scheduler.schedule_test(test)

    # Run tests
    results = await runner.run_tests()

    # Get node loads
    node_loads = scheduler.get_node_loads()

    # Verify load distribution
    assert len(node_loads) == len(test_environment["nodes"])
    max_load = max(node_loads.values())
    min_load = min(node_loads.values())
    assert max_load - min_load <= 1  # Load should be balanced within 1 test


@pytest.mark.asyncio
async def test_result_aggregation(test_environment):
    """Test result aggregation and analysis."""
    runner = test_environment["runner"]
    scheduler = test_environment["scheduler"]
    aggregator = test_environment["aggregator"]

    # Define tests with metrics
    tests = [
        {
            "id": f"test_{i}",
            "name": "test_metrics",
            "type": "api",
            "priority": "high",
            "metrics": ["response_time", "memory_usage"],
        }
        for i in range(10)
    ]

    # Schedule and run tests
    for test in tests:
        await scheduler.schedule_test(test)
    results = await runner.run_tests()

    # Add results to aggregator
    for result in results:
        aggregator.add_result(result)

    # Verify aggregation
    summary = aggregator.get_summary()
    assert summary["total_tests"] == len(tests)
    assert summary["passed"] == len(tests)

    # Verify metrics
    metrics = aggregator.get_metrics_summary()
    assert "response_time" in metrics
    assert "memory_usage" in metrics


@pytest.mark.asyncio
async def test_priority_based_execution(test_environment):
    """Test priority-based test execution."""
    runner = test_environment["runner"]
    scheduler = test_environment["scheduler"]

    # Define tests with different priorities
    tests = [
        {
            "id": f"test_{i}",
            "name": "test_priority",
            "type": "api",
            "priority": priority,
            "duration": 1.0,
        }
        for i, priority in enumerate(
            ["critical"] * 5 + ["high"] * 10 + ["medium"] * 15 + ["low"] * 20
        )
    ]

    # Schedule tests
    for test in tests:
        await scheduler.schedule_test(test)

    # Run tests
    results = await runner.run_tests()

    # Verify execution order (critical and high priority tests should complete first)
    critical_results = [
        r
        for r in results
        if r.test_id.startswith("test_") and int(r.test_id.split("_")[1]) < 5
    ]
    high_results = [
        r
        for r in results
        if r.test_id.startswith("test_") and 5 <= int(r.test_id.split("_")[1]) < 15
    ]

    # Get completion times
    critical_times = [r.timestamp for r in critical_results]
    high_times = [r.timestamp for r in high_results]

    # Verify priority order
    assert max(critical_times) < min(high_times)
