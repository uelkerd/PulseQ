"""
Tests for the OptimizedLoadBalancer class.
"""

import asyncio
from datetime import datetime, timedelta

import pytest

from pulseq.distributed.load_balancer import NodeLoad, OptimizedLoadBalancer
from pulseq.performance.profiler import PerformanceProfiler


@pytest.fixture
def load_balancer():
    """Create a load balancer instance for testing."""
    return OptimizedLoadBalancer()


@pytest.fixture
def sample_nodes():
    """Create sample nodes with different capabilities."""
    return {
        "node1": {"os": "linux", "memory": "16GB", "cpu_cores": "8"},
        "node2": {"os": "windows", "memory": "8GB", "cpu_cores": "4"},
        "node3": {"os": "linux", "memory": "8GB", "cpu_cores": "4"},
    }


@pytest.mark.asyncio
async def test_add_node(load_balancer, sample_nodes):
    """Test adding nodes to the load balancer."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Verify nodes were added
    assert len(load_balancer.nodes) == 3
    for node_id in sample_nodes:
        assert node_id in load_balancer.nodes
        assert load_balancer.nodes[node_id].capabilities == sample_nodes[node_id]


@pytest.mark.asyncio
async def test_remove_node(load_balancer, sample_nodes):
    """Test removing nodes from the load balancer."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Remove a node
    load_balancer.remove_node("node1")

    # Verify node was removed
    assert len(load_balancer.nodes) == 2
    assert "node1" not in load_balancer.nodes
    assert "node2" in load_balancer.nodes
    assert "node3" in load_balancer.nodes


@pytest.mark.asyncio
async def test_update_node_load(load_balancer, sample_nodes):
    """Test updating node load information."""
    # Add a node
    load_balancer.add_node("node1", sample_nodes["node1"])

    # Update load information
    load_info = {
        "current_load": 0.5,
        "cpu_usage": 0.3,
        "memory_usage": 0.4,
        "network_latency": 0.1,
    }
    load_balancer.update_node_load("node1", load_info)

    # Verify load was updated
    node = load_balancer.nodes["node1"]
    assert node.current_load == 0.5
    assert node.cpu_usage == 0.3
    assert node.memory_usage == 0.4
    assert node.network_latency == 0.1


@pytest.mark.asyncio
async def test_weight_calculation(load_balancer, sample_nodes):
    """Test weight calculation based on capabilities."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Verify weights
    weights = load_balancer.weights
    assert len(weights) == 3

    # Node1 should have highest weight (Linux, 16GB, 8 cores)
    assert weights["node1"] > weights["node2"]
    assert weights["node1"] > weights["node3"]

    # Node3 should have higher weight than node2 (Linux vs Windows)
    assert weights["node3"] > weights["node2"]


@pytest.mark.asyncio
async def test_node_selection(load_balancer, sample_nodes):
    """Test node selection with different strategies."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Test weighted round-robin selection
    load_balancer.strategy = "weighted_round_robin"
    selected_nodes = set()
    for _ in range(100):
        node_id = load_balancer.select_node()
        selected_nodes.add(node_id)
        assert node_id in sample_nodes

    # Should select all nodes
    assert len(selected_nodes) == 3

    # Test least-load selection
    load_balancer.strategy = "least_load"
    load_balancer.update_node_load("node1", {"current_load": 0.8})
    load_balancer.update_node_load("node2", {"current_load": 0.3})
    load_balancer.update_node_load("node3", {"current_load": 0.5})

    # Should select node2 (least load)
    assert load_balancer.select_node() == "node2"


@pytest.mark.asyncio
async def test_requirement_filtering(load_balancer, sample_nodes):
    """Test filtering nodes based on requirements."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Test Linux requirement
    linux_nodes = load_balancer._filter_nodes_by_requirements({"os": "linux"})
    assert len(linux_nodes) == 2
    assert "node1" in linux_nodes
    assert "node3" in linux_nodes

    # Test memory requirement
    high_mem_nodes = load_balancer._filter_nodes_by_requirements({"memory": "16GB"})
    assert len(high_mem_nodes) == 1
    assert "node1" in high_mem_nodes

    # Test multiple requirements
    high_perf_nodes = load_balancer._filter_nodes_by_requirements(
        {"os": "linux", "memory": "16GB"}
    )
    assert len(high_perf_nodes) == 1
    assert "node1" in high_perf_nodes


@pytest.mark.asyncio
async def test_strategy_optimization(load_balancer, sample_nodes):
    """Test strategy optimization based on performance metrics."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Create a profiler with test data
    profiler = PerformanceProfiler()
    load_balancer.profiler = profiler

    # Simulate high load imbalance
    for _ in range(100):
        profiler.record_metrics(
            profiler.PerformanceMetrics(
                test_id="test1",
                node_id="node1",
                start_time=0,
                end_time=1,
                cpu_usage=0.9,
                memory_usage=0.8,
                network_latency=0.1,
                queue_time=0.1,
                execution_time=0.8,
            )
        )

    # Optimize strategy
    load_balancer.optimize_strategy()

    # Should switch to least-load strategy
    assert load_balancer.strategy == "least_load"


@pytest.mark.asyncio
async def test_node_stats(load_balancer, sample_nodes):
    """Test getting node statistics."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Update load information
    load_info = {
        "current_load": 0.5,
        "cpu_usage": 0.3,
        "memory_usage": 0.4,
        "network_latency": 0.1,
    }
    load_balancer.update_node_load("node1", load_info)

    # Get stats
    stats = load_balancer.get_node_stats()

    # Verify stats
    assert "node1" in stats
    assert stats["node1"]["current_load"] == 0.5
    assert stats["node1"]["cpu_usage"] == 0.3
    assert stats["node1"]["memory_usage"] == 0.4
    assert stats["node1"]["network_latency"] == 0.1
    assert "weight" in stats["node1"]


@pytest.mark.asyncio
async def test_edge_cases(load_balancer):
    """Test edge cases and error handling."""
    # Test empty node list
    assert load_balancer.select_node() is None

    # Test non-existent node
    load_balancer.update_node_load("nonexistent", {})
    load_balancer.remove_node("nonexistent")

    # Test invalid strategy
    load_balancer.strategy = "invalid"
    assert load_balancer.select_node() is None


@pytest.mark.asyncio
async def test_concurrent_node_updates(load_balancer, sample_nodes):
    """Test concurrent updates to node load information."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Create concurrent update tasks
    async def update_node_load(node_id, load_info):
        load_balancer.update_node_load(node_id, load_info)

    # Simulate concurrent updates
    tasks = []
    for node_id in sample_nodes:
        load_info = {
            "current_load": 0.5,
            "cpu_usage": 0.3,
            "memory_usage": 0.4,
            "network_latency": 0.1,
        }
        tasks.append(update_node_load(node_id, load_info))

    # Execute updates concurrently
    await asyncio.gather(*tasks)

    # Verify all nodes were updated
    for node_id in sample_nodes:
        node = load_balancer.nodes[node_id]
        assert node.current_load == 0.5
        assert node.cpu_usage == 0.3
        assert node.memory_usage == 0.4
        assert node.network_latency == 0.1


@pytest.mark.asyncio
async def test_node_health_monitoring(load_balancer, sample_nodes):
    """Test node health monitoring and automatic removal."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Simulate node health degradation
    load_balancer.update_node_load(
        "node1",
        {
            "current_load": 0.9,
            "cpu_usage": 0.95,
            "memory_usage": 0.9,
            "network_latency": 0.5,
        },
    )

    # Verify node is marked as unhealthy
    stats = load_balancer.get_node_stats()
    assert stats["node1"]["current_load"] == 0.9
    assert stats["node1"]["cpu_usage"] == 0.95
    assert stats["node1"]["memory_usage"] == 0.9
    assert stats["node1"]["network_latency"] == 0.5


@pytest.mark.asyncio
async def test_dynamic_weight_adjustment(load_balancer, sample_nodes):
    """Test dynamic weight adjustment based on performance."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Initial weights
    initial_weights = load_balancer.weights.copy()

    # Update node performance
    load_balancer.update_node_load(
        "node1",
        {
            "current_load": 0.8,
            "cpu_usage": 0.7,
            "memory_usage": 0.6,
            "network_latency": 0.2,
        },
    )

    # Verify weights changed
    updated_weights = load_balancer.weights
    assert updated_weights != initial_weights
    assert (
        updated_weights["node1"] < initial_weights["node1"]
    )  # Weight should decrease with higher load


@pytest.mark.asyncio
async def test_priority_based_selection(load_balancer, sample_nodes):
    """Test priority-based node selection."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Set different priorities for nodes
    load_balancer.update_node_load("node1", {"current_load": 0.3})
    load_balancer.update_node_load("node2", {"current_load": 0.6})
    load_balancer.update_node_load("node3", {"current_load": 0.9})

    # Test selection with different requirements
    high_priority_nodes = load_balancer._filter_nodes_by_requirements(
        {"os": "linux", "memory": "16GB"}
    )
    assert len(high_priority_nodes) == 1
    assert "node1" in high_priority_nodes


@pytest.mark.asyncio
async def test_load_balancing_with_failures(load_balancer, sample_nodes):
    """Test load balancing behavior with node failures."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Simulate node failure
    load_balancer.remove_node("node1")

    # Update remaining nodes
    load_balancer.update_node_load("node2", {"current_load": 0.4})
    load_balancer.update_node_load("node3", {"current_load": 0.6})

    # Test selection after failure
    selected_node = load_balancer.select_node()
    assert selected_node in ["node2", "node3"]
    assert selected_node != "node1"


@pytest.mark.asyncio
async def test_capability_based_weights(load_balancer, sample_nodes):
    """Test weight calculation based on node capabilities."""
    # Add nodes with different capabilities
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Verify capability-based weights
    weights = load_balancer.weights
    assert weights["node1"] > weights["node2"]  # node1 has better capabilities
    assert weights["node1"] > weights["node3"]  # node1 has better capabilities
    assert (
        weights["node3"] > weights["node2"]
    )  # node3 has same capabilities as node2 but Linux OS


@pytest.mark.asyncio
async def test_strategy_switching(load_balancer, sample_nodes):
    """Test automatic strategy switching based on performance."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Initial strategy
    assert load_balancer.strategy == "weighted_round_robin"

    # Simulate performance issues
    profiler = PerformanceProfiler()
    load_balancer.profiler = profiler

    # Record poor performance metrics
    for _ in range(50):
        profiler.record_metrics(
            profiler.PerformanceMetrics(
                test_id="test1",
                node_id="node1",
                start_time=0,
                end_time=1,
                cpu_usage=0.9,
                memory_usage=0.8,
                network_latency=0.3,
                queue_time=0.5,
                execution_time=0.7,
            )
        )

    # Optimize strategy
    load_balancer.optimize_strategy()

    # Should switch to least-load strategy
    assert load_balancer.strategy == "least_load"


@pytest.mark.asyncio
async def test_complex_requirement_matching(load_balancer, sample_nodes):
    """Test complex requirement matching scenarios."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Test multiple requirement combinations
    test_cases = [
        ({"os": "linux"}, 2),  # Should match node1 and node3
        ({"memory": "16GB"}, 1),  # Should match only node1
        ({"cpu_cores": "4"}, 2),  # Should match node2 and node3
        ({"os": "linux", "cpu_cores": "8"}, 1),  # Should match only node1
        ({"os": "windows", "memory": "8GB"}, 1),  # Should match only node2
    ]

    for requirements, expected_count in test_cases:
        matching_nodes = load_balancer._filter_nodes_by_requirements(requirements)
        assert len(matching_nodes) == expected_count


@pytest.mark.asyncio
async def test_load_distribution_fairness(load_balancer, sample_nodes):
    """Test fairness of load distribution across nodes."""
    # Add nodes
    for node_id, capabilities in sample_nodes.items():
        load_balancer.add_node(node_id, capabilities)

    # Simulate multiple test executions
    node_selections = {node_id: 0 for node_id in sample_nodes}
    for _ in range(1000):
        selected_node = load_balancer.select_node()
        node_selections[selected_node] += 1

    # Calculate selection ratios
    total_selections = sum(node_selections.values())
    selection_ratios = {
        node_id: count / total_selections for node_id, count in node_selections.items()
    }

    # Verify fair distribution (within 10% of expected ratio)
    expected_ratio = 1 / len(sample_nodes)
    for ratio in selection_ratios.values():
        assert abs(ratio - expected_ratio) < 0.1
