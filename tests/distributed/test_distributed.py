"""
Test cases for distributed testing components.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from pulseq.distributed.test_runner import DistributedTestRunner, TestNode
from pulseq.distributed.node_manager import NodeManager
from pulseq.distributed.test_scheduler import TestScheduler
from pulseq.distributed.results_aggregator import ResultsAggregator, TestResult

@pytest.fixture
def test_runner():
    """Create a test runner instance."""
    return DistributedTestRunner()

@pytest.fixture
def node_manager():
    """Create a node manager instance."""
    return NodeManager()

@pytest.fixture
def test_scheduler():
    """Create a test scheduler instance."""
    return TestScheduler()

@pytest.fixture
def results_aggregator():
    """Create a results aggregator instance."""
    return ResultsAggregator()

@pytest.fixture
def sample_nodes():
    """Create sample test nodes."""
    return [
        TestNode("node1", "localhost", 8000),
        TestNode("node2", "localhost", 8001),
        TestNode("node3", "localhost", 8002)
    ]

@pytest.fixture
def sample_tests():
    """Create sample test cases."""
    return [
        {"id": "test1", "name": "test_api_endpoint", "duration": 1.0, "priority": "high"},
        {"id": "test2", "name": "test_database", "duration": 2.0, "priority": "medium"},
        {"id": "test3", "name": "test_cache", "duration": 0.5, "priority": "low"},
        {"id": "test4", "name": "test_performance", "duration": 3.0, "priority": "high"}
    ]

@pytest.mark.asyncio
async def test_node_registration(test_runner, sample_nodes):
    """Test node registration functionality."""
    for node in sample_nodes:
        await test_runner.add_node(node)
        
    assert len(test_runner.nodes) == len(sample_nodes)
    assert all(node.id in test_runner.nodes for node in sample_nodes)
    
    # Test duplicate node registration
    with pytest.raises(ValueError):
        await test_runner.add_node(sample_nodes[0])

@pytest.mark.asyncio
async def test_node_removal(test_runner, sample_nodes):
    """Test node removal functionality."""
    # Register nodes
    for node in sample_nodes:
        await test_runner.add_node(node)
    
    # Remove a node
    await test_runner.remove_node(sample_nodes[0].id)
    assert sample_nodes[0].id not in test_runner.nodes
    assert len(test_runner.nodes) == len(sample_nodes) - 1
    
    # Test removing non-existent node
    with pytest.raises(KeyError):
        await test_runner.remove_node("non_existent_node")

@pytest.mark.asyncio
async def test_test_distribution(test_runner, test_scheduler, sample_nodes, sample_tests):
    """Test test distribution functionality."""
    # Register nodes
    for node in sample_nodes:
        await test_runner.add_node(node)
        
    # Schedule tests
    for test in sample_tests:
        await test_scheduler.schedule_test(test)
        
    # Distribute tests
    await test_runner.distribute_tests(test_scheduler)
    
    # Verify test distribution
    for node in sample_nodes:
        node_tests = test_scheduler.get_node_tests(node.id)
        assert len(node_tests) > 0
        # Verify priority-based distribution
        if node.id == "node1":  # Assuming node1 gets high priority tests
            assert any(test["priority"] == "high" for test in node_tests)

@pytest.mark.asyncio
async def test_node_health_monitoring(node_manager, sample_nodes):
    """Test node health monitoring."""
    # Register nodes
    for node in sample_nodes:
        await node_manager.register_node(node)
        
    # Start monitoring
    await node_manager.start_monitoring()
    
    # Simulate heartbeats
    for node in sample_nodes:
        await node_manager.process_heartbeat(node.id)
        
    # Verify node status
    for node in sample_nodes:
        assert node_manager.get_node_status(node.id) == "active"
    
    # Simulate node timeout
    await asyncio.sleep(node_manager.node_timeout + 1)
    assert node_manager.get_node_status(sample_nodes[0].id) == "inactive"

@pytest.mark.asyncio
async def test_results_aggregation(results_aggregator):
    """Test results aggregation functionality."""
    # Create sample results
    results = [
        TestResult(
            test_id="test1",
            node_id="node1",
            status="passed",
            duration=1.0,
            timestamp=datetime.now(),
            metrics={"response_time": 0.5, "memory_usage": 100}
        ),
        TestResult(
            test_id="test2",
            node_id="node2",
            status="failed",
            duration=2.0,
            timestamp=datetime.now(),
            error="Connection timeout",
            metrics={"response_time": 1.0, "memory_usage": 150}
        ),
        TestResult(
            test_id="test3",
            node_id="node1",
            status="error",
            duration=0.5,
            timestamp=datetime.now(),
            error="Runtime error",
            metrics={"response_time": 0.3, "memory_usage": 200}
        )
    ]
    
    # Add results
    for result in results:
        results_aggregator.add_result(result)
        
    # Verify results
    assert len(results_aggregator.get_results()) == len(results)
    
    # Verify summary
    summary = results_aggregator.get_summary()
    assert summary["total_tests"] == len(results)
    assert summary["passed"] == 1
    assert summary["failed"] == 1
    assert summary["errors"] == 1
    assert summary["pass_rate"] == (1/3) * 100
    
    # Verify node-specific summary
    node_summary = results_aggregator.get_node_summary("node1")
    assert node_summary["total_tests"] == 2
    assert node_summary["passed"] == 1
    assert node_summary["errors"] == 1
    
    # Verify metrics
    metrics = results_aggregator.get_metrics_summary()
    assert "response_time" in metrics
    assert metrics["response_time"]["min"] == 0.3
    assert metrics["response_time"]["max"] == 1.0
    assert metrics["response_time"]["avg"] == 0.6
    assert "memory_usage" in metrics
    assert metrics["memory_usage"]["min"] == 100
    assert metrics["memory_usage"]["max"] == 200

@pytest.mark.asyncio
async def test_load_balancing(test_scheduler, sample_nodes, sample_tests):
    """Test load balancing functionality."""
    # Register nodes
    for node in sample_nodes:
        await test_scheduler.register_node(node)
        
    # Schedule tests
    for test in sample_tests:
        await test_scheduler.schedule_test(test)
        
    # Verify load distribution
    node_loads = test_scheduler.get_node_loads()
    assert len(node_loads) == len(sample_nodes)
    
    # Verify load balancing
    max_load = max(node_loads.values())
    min_load = min(node_loads.values())
    assert max_load - min_load <= 1  # Load should be balanced within 1 test
    
    # Verify priority-based load balancing
    high_priority_tests = [test for test in sample_tests if test["priority"] == "high"]
    assert any(node_loads[node.id] >= len(high_priority_tests) for node in sample_nodes)

@pytest.mark.asyncio
async def test_error_handling(test_runner, test_scheduler, results_aggregator):
    """Test error handling in distributed testing."""
    # Create a failing test
    failing_test = {
        "id": "failing_test",
        "name": "test_error_handling",
        "duration": 1.0
    }
    
    # Schedule and run test
    await test_scheduler.schedule_test(failing_test)
    result = await test_runner.run_test(failing_test)
    
    # Verify error handling
    assert result.status == "error"
    assert result.error is not None
    
    # Verify result aggregation
    results_aggregator.add_result(result)
    summary = results_aggregator.get_summary()
    assert summary["errors"] == 1

@pytest.mark.asyncio
async def test_concurrent_test_execution(test_runner, test_scheduler, sample_nodes, sample_tests):
    """Test concurrent test execution."""
    # Register nodes
    for node in sample_nodes:
        await test_runner.add_node(node)
    
    # Schedule tests
    for test in sample_tests:
        await test_scheduler.schedule_test(test)
    
    # Run tests concurrently
    tasks = []
    for test in sample_tests:
        task = asyncio.create_task(test_runner.run_test(test))
        tasks.append(task)
    
    # Wait for all tests to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Verify results
    assert len(results) == len(sample_tests)
    assert all(isinstance(result, TestResult) for result in results)

@pytest.mark.asyncio
async def test_test_retry_mechanism(test_runner, test_scheduler):
    """Test test retry mechanism."""
    # Create a test that fails initially but passes on retry
    test = {
        "id": "retry_test",
        "name": "test_retry",
        "duration": 1.0,
        "max_retries": 2
    }
    
    # Run test with retries
    result = await test_runner.run_test_with_retry(test)
    
    # Verify retry behavior
    assert result.attempts <= test["max_retries"]
    assert result.status in ["passed", "failed", "error"]

@pytest.mark.asyncio
async def test_node_capability_matching(test_runner, test_scheduler, sample_nodes):
    """Test node capability matching."""
    # Add capabilities to nodes
    sample_nodes[0].capabilities = {"os": "linux", "browser": "chrome"}
    sample_nodes[1].capabilities = {"os": "windows", "browser": "firefox"}
    sample_nodes[2].capabilities = {"os": "macos", "browser": "safari"}
    
    # Create a test with specific requirements
    test = {
        "id": "capability_test",
        "name": "test_capabilities",
        "duration": 1.0,
        "requirements": {"os": "linux", "browser": "chrome"}
    }
    
    # Schedule and distribute test
    await test_scheduler.schedule_test(test)
    await test_runner.distribute_tests(test_scheduler)
    
    # Verify test was assigned to matching node
    node_tests = test_scheduler.get_node_tests(sample_nodes[0].id)
    assert any(t["id"] == test["id"] for t in node_tests)

@pytest.mark.asyncio
async def test_test_timeout_handling(test_runner, test_scheduler):
    """Test test timeout handling."""
    # Create a test that exceeds timeout
    test = {
        "id": "timeout_test",
        "name": "test_timeout",
        "duration": 10.0,
        "timeout": 1.0
    }
    
    # Run test
    result = await test_runner.run_test(test)
    
    # Verify timeout handling
    assert result.status == "error"
    assert "timeout" in result.error.lower() 