"""
Performance benchmarks for the OptimizedLoadBalancer class.
"""

import pytest
import time
import asyncio
import statistics
from datetime import datetime
from pulseq.distributed.load_balancer import OptimizedLoadBalancer
from pulseq.performance.profiler import PerformanceProfiler
import numpy as np
from pulseq.distributed.node import Node
from pulseq.distributed.strategy import LoadBalancingStrategy
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy.stats import adfuller, ttest_ind, mannwhitneyu, spearmanr, kendalltau, skew, kurtosis, shapiro
from pulseq.visualization.resource_visualizer import ResourceVisualizer

@pytest.fixture
def benchmark_load_balancer():
    """Create a load balancer instance for benchmarking."""
    return OptimizedLoadBalancer()

@pytest.fixture
def large_node_set():
    """Create a large set of nodes with varying capabilities."""
    nodes = {}
    for i in range(100):  # 100 nodes
        node_id = f"node{i}"
        nodes[node_id] = {
            "os": "linux" if i % 2 == 0 else "windows",
            "memory": "16GB" if i % 3 == 0 else "8GB",
            "cpu_cores": "8" if i % 4 == 0 else "4"
        }
    return nodes

def benchmark_node_selection(benchmark_load_balancer, num_selections=1000):
    """Benchmark node selection performance."""
    start_time = time.time()
    for _ in range(num_selections):
        benchmark_load_balancer.select_node()
    end_time = time.time()
    return (end_time - start_time) / num_selections

def benchmark_weight_calculation(benchmark_load_balancer, num_updates=100):
    """Benchmark weight calculation performance."""
    start_time = time.time()
    for _ in range(num_updates):
        benchmark_load_balancer._update_weights()
    end_time = time.time()
    return (end_time - start_time) / num_updates

def benchmark_concurrent_updates(benchmark_load_balancer, num_nodes=100, num_updates=1000):
    """Benchmark concurrent node updates."""
    async def update_node(node_id):
        load_info = {
            "current_load": 0.5,
            "cpu_usage": 0.3,
            "memory_usage": 0.4,
            "network_latency": 0.1
        }
        benchmark_load_balancer.update_node_load(node_id, load_info)
    
    start_time = time.time()
    tasks = []
    for _ in range(num_updates):
        node_id = f"node{_ % num_nodes}"
        tasks.append(update_node(node_id))
    asyncio.run(asyncio.gather(*tasks))
    end_time = time.time()
    return (end_time - start_time) / num_updates

@pytest.mark.benchmark
def test_node_selection_performance(benchmark_load_balancer, large_node_set):
    """Benchmark node selection performance with varying node counts."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Measure selection time
    selection_times = []
    for _ in range(10):  # Run 10 times for statistical significance
        avg_time = benchmark_node_selection(benchmark_load_balancer)
        selection_times.append(avg_time)
    
    # Calculate statistics
    mean_time = statistics.mean(selection_times)
    std_dev = statistics.stdev(selection_times)
    
    # Log results
    print(f"\nNode Selection Performance:")
    print(f"Mean time per selection: {mean_time * 1000:.3f} ms")
    print(f"Standard deviation: {std_dev * 1000:.3f} ms")
    
    # Assert performance requirements
    assert mean_time < 0.001  # Should take less than 1ms per selection

@pytest.mark.benchmark
def test_weight_calculation_performance(benchmark_load_balancer, large_node_set):
    """Benchmark weight calculation performance."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Measure calculation time
    calculation_times = []
    for _ in range(10):
        avg_time = benchmark_weight_calculation(benchmark_load_balancer)
        calculation_times.append(avg_time)
    
    # Calculate statistics
    mean_time = statistics.mean(calculation_times)
    std_dev = statistics.stdev(calculation_times)
    
    # Log results
    print(f"\nWeight Calculation Performance:")
    print(f"Mean time per calculation: {mean_time * 1000:.3f} ms")
    print(f"Standard deviation: {std_dev * 1000:.3f} ms")
    
    # Assert performance requirements
    assert mean_time < 0.01  # Should take less than 10ms per calculation

@pytest.mark.benchmark
def test_concurrent_update_performance(benchmark_load_balancer, large_node_set):
    """Benchmark concurrent node update performance."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Measure update time
    update_times = []
    for _ in range(5):  # Run 5 times due to longer execution time
        avg_time = benchmark_concurrent_updates(benchmark_load_balancer)
        update_times.append(avg_time)
    
    # Calculate statistics
    mean_time = statistics.mean(update_times)
    std_dev = statistics.stdev(update_times)
    
    # Log results
    print(f"\nConcurrent Update Performance:")
    print(f"Mean time per update: {mean_time * 1000:.3f} ms")
    print(f"Standard deviation: {std_dev * 1000:.3f} ms")
    
    # Assert performance requirements
    assert mean_time < 0.005  # Should take less than 5ms per update

@pytest.mark.benchmark
def test_memory_usage(benchmark_load_balancer, large_node_set):
    """Benchmark memory usage with large node sets."""
    import psutil
    import os
    
    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Get final memory usage
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    # Log results
    print(f"\nMemory Usage:")
    print(f"Initial memory: {initial_memory:.2f} MB")
    print(f"Final memory: {final_memory:.2f} MB")
    print(f"Memory increase: {memory_increase:.2f} MB")
    
    # Assert memory requirements
    assert memory_increase < 50  # Should use less than 50MB for 100 nodes

@pytest.mark.benchmark
def test_load_distribution_efficiency(benchmark_load_balancer, large_node_set):
    """Benchmark load distribution efficiency."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Simulate load distribution
    node_loads = {node_id: 0 for node_id in large_node_set}
    num_tests = 10000
    
    start_time = time.time()
    for _ in range(num_tests):
        selected_node = benchmark_load_balancer.select_node()
        node_loads[selected_node] += 1
    end_time = time.time()
    
    # Calculate distribution metrics
    loads = list(node_loads.values())
    mean_load = statistics.mean(loads)
    std_dev = statistics.stdev(loads)
    cv = (std_dev / mean_load) * 100  # Coefficient of variation
    
    # Log results
    print(f"\nLoad Distribution Efficiency:")
    print(f"Total time: {end_time - start_time:.3f} s")
    print(f"Mean load per node: {mean_load:.2f}")
    print(f"Standard deviation: {std_dev:.2f}")
    print(f"Coefficient of variation: {cv:.2f}%")
    
    # Assert distribution requirements
    assert cv < 20  # Load should be distributed with less than 20% variation

@pytest.mark.benchmark
def test_scalability_with_node_count(benchmark_load_balancer):
    """Benchmark performance with increasing number of nodes."""
    node_counts = [10, 50, 100, 200, 500]
    results = []
    
    for count in node_counts:
        # Create nodes
        nodes = {
            f"node{i}": {
                "os": "linux" if i % 2 == 0 else "windows",
                "memory": "16GB" if i % 3 == 0 else "8GB",
                "cpu_cores": "8" if i % 4 == 0 else "4"
            }
            for i in range(count)
        }
        
        # Add nodes
        for node_id, capabilities in nodes.items():
            benchmark_load_balancer.add_node(node_id, capabilities)
        
        # Measure selection time
        selection_times = []
        for _ in range(5):
            avg_time = benchmark_node_selection(benchmark_load_balancer)
            selection_times.append(avg_time)
        
        mean_time = statistics.mean(selection_times)
        results.append((count, mean_time))
        
        # Clear nodes for next iteration
        benchmark_load_balancer.nodes.clear()
    
    # Log results
    print("\nScalability Results:")
    for count, time in results:
        print(f"Nodes: {count}, Mean selection time: {time * 1000:.3f} ms")
    
    # Assert scalability requirements
    for count, time in results:
        assert time < 0.001 * (count / 100)  # Linear scaling factor

@pytest.mark.benchmark
def test_stress_testing(benchmark_load_balancer, large_node_set):
    """Stress test the load balancer with high load conditions."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Simulate high load conditions
    async def stress_node(node_id):
        for _ in range(100):
            load_info = {
                "current_load": 0.9,
                "cpu_usage": 0.95,
                "memory_usage": 0.9,
                "network_latency": 0.5
            }
            benchmark_load_balancer.update_node_load(node_id, load_info)
            await asyncio.sleep(0.001)  # Small delay to simulate real conditions
    
    # Run stress test
    start_time = time.time()
    tasks = [stress_node(node_id) for node_id in large_node_set]
    asyncio.run(asyncio.gather(*tasks))
    end_time = time.time()
    
    # Log results
    print(f"\nStress Test Results:")
    print(f"Total time: {end_time - start_time:.3f} s")
    print(f"Updates per second: {len(large_node_set) * 100 / (end_time - start_time):.2f}")
    
    # Assert stress test requirements
    assert (end_time - start_time) < 10  # Should complete within 10 seconds

@pytest.mark.benchmark
def test_workload_patterns(benchmark_load_balancer, large_node_set):
    """Test performance with different workload patterns."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    patterns = [
        ("burst", [(0.9, 100), (0.1, 100)]),  # Burst pattern
        ("gradual", [(0.1, 50), (0.5, 50), (0.9, 50)]),  # Gradual increase
        ("spike", [(0.1, 50), (0.9, 10), (0.1, 50)]),  # Spike pattern
    ]
    
    results = {}
    for pattern_name, load_steps in patterns:
        start_time = time.time()
        for load, count in load_steps:
            for _ in range(count):
                node_id = benchmark_load_balancer.select_node()
                load_info = {
                    "current_load": load,
                    "cpu_usage": load * 0.9,
                    "memory_usage": load * 0.8,
                    "network_latency": load * 0.2
                }
                benchmark_load_balancer.update_node_load(node_id, load_info)
        end_time = time.time()
        results[pattern_name] = end_time - start_time
    
    # Log results
    print("\nWorkload Pattern Results:")
    for pattern, time_taken in results.items():
        print(f"Pattern: {pattern}, Time: {time_taken:.3f} s")
    
    # Assert pattern requirements
    for time_taken in results.values():
        assert time_taken < 5  # Should handle each pattern within 5 seconds

@pytest.mark.benchmark
def test_strategy_switching_performance(benchmark_load_balancer, large_node_set):
    """Benchmark performance of strategy switching."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Create profiler with test data
    profiler = PerformanceProfiler()
    benchmark_load_balancer.profiler = profiler
    
    # Measure strategy switching time
    switch_times = []
    for _ in range(10):
        # Record metrics to trigger strategy change
        for _ in range(50):
            profiler.record_metrics(profiler.PerformanceMetrics(
                test_id="test1",
                node_id="node1",
                start_time=0,
                end_time=1,
                cpu_usage=0.9,
                memory_usage=0.8,
                network_latency=0.3,
                queue_time=0.5,
                execution_time=0.7
            ))
        
        # Time strategy optimization
        start_time = time.time()
        benchmark_load_balancer.optimize_strategy()
        end_time = time.time()
        switch_times.append(end_time - start_time)
    
    # Calculate statistics
    mean_time = statistics.mean(switch_times)
    std_dev = statistics.stdev(switch_times)
    
    # Log results
    print(f"\nStrategy Switching Performance:")
    print(f"Mean switch time: {mean_time * 1000:.3f} ms")
    print(f"Standard deviation: {std_dev * 1000:.3f} ms")
    
    # Assert switching requirements
    assert mean_time < 0.1  # Should switch strategies in less than 100ms

@pytest.mark.benchmark
def test_mixed_workload_performance(benchmark_load_balancer, large_node_set):
    """Test performance with mixed workload types."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Define workload types
    workloads = [
        ("api", {"type": "api", "priority": "high"}),
        ("ui", {"type": "ui", "priority": "medium"}),
        ("performance", {"type": "performance", "priority": "low"})
    ]
    
    results = {}
    for workload_name, requirements in workloads:
        start_time = time.time()
        for _ in range(1000):
            benchmark_load_balancer.select_node(requirements)
        end_time = time.time()
        results[workload_name] = end_time - start_time
    
    # Log results
    print("\nMixed Workload Performance:")
    for workload, time_taken in results.items():
        print(f"Workload: {workload}, Time: {time_taken:.3f} s")
    
    # Assert mixed workload requirements
    for time_taken in results.values():
        assert time_taken < 1  # Should handle each workload type within 1 second

@pytest.mark.benchmark
def test_strategy_specific_workloads(benchmark_load_balancer, large_node_set):
    """Test performance with strategy-specific workload patterns."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Define workload patterns for each strategy
    workloads = {
        "least_connections": [
            # Simulate long-running tests with varying durations
            {"duration": 30, "connections": 5, "count": 50},  # Long tests
            {"duration": 10, "connections": 3, "count": 100},  # Medium tests
            {"duration": 5, "connections": 1, "count": 200}    # Short tests
        ],
        "response_time": [
            # Simulate tests with varying response time requirements
            {"response_time": 0.1, "variance": 0.05, "count": 100},  # Fast tests
            {"response_time": 0.5, "variance": 0.1, "count": 100},   # Medium tests
            {"response_time": 1.0, "variance": 0.2, "count": 100}    # Slow tests
        ],
        "predictive": [
            # Simulate tests with predictable load patterns
            {"load_pattern": "linear", "start": 0.1, "end": 0.9, "count": 100},  # Linear increase
            {"load_pattern": "spike", "base": 0.2, "spike": 0.8, "count": 100},  # Spikes
            {"load_pattern": "periodic", "min": 0.1, "max": 0.7, "count": 100}   # Periodic
        ]
    }
    
    results = {}
    for strategy, patterns in workloads.items():
        benchmark_load_balancer.strategy = strategy
        strategy_results = []
        
        for pattern in patterns:
            start_time = time.time()
            
            if strategy == "least_connections":
                # Simulate connections
                for _ in range(pattern["count"]):
                    node_id = benchmark_load_balancer.select_node()
                    if node_id:
                        node = benchmark_load_balancer.nodes[node_id]
                        node.active_connections += pattern["connections"]
                        time.sleep(pattern["duration"] / 1000)  # Simulate test duration
                        node.active_connections -= pattern["connections"]
            
            elif strategy == "response_time":
                # Simulate response times
                for _ in range(pattern["count"]):
                    node_id = benchmark_load_balancer.select_node()
                    if node_id:
                        response_time = np.random.normal(
                            pattern["response_time"],
                            pattern["variance"]
                        )
                        benchmark_load_balancer.update_node_load(
                            node_id,
                            {"response_time": max(0.01, response_time)}
                        )
            
            elif strategy == "predictive":
                # Simulate load patterns
                for _ in range(pattern["count"]):
                    node_id = benchmark_load_balancer.select_node()
                    if node_id:
                        if pattern["load_pattern"] == "linear":
                            load = pattern["start"] + (pattern["end"] - pattern["start"]) * (_ / pattern["count"])
                        elif pattern["load_pattern"] == "spike":
                            load = pattern["base"] if _ % 10 != 0 else pattern["spike"]
                        else:  # periodic
                            load = pattern["min"] + (pattern["max"] - pattern["min"]) * (np.sin(_ / 10) + 1) / 2
                        
                        benchmark_load_balancer.update_node_load(
                            node_id,
                            {"current_load": load}
                        )
            
            end_time = time.time()
            strategy_results.append({
                "pattern": pattern,
                "time_taken": end_time - start_time,
                "throughput": pattern["count"] / (end_time - start_time)
            })
        
        results[strategy] = strategy_results
    
    # Log results
    print("\nStrategy-Specific Workload Results:")
    for strategy, strategy_results in results.items():
        print(f"\n{strategy.upper()} Strategy:")
        for result in strategy_results:
            print(f"Pattern: {result['pattern']}")
            print(f"Time taken: {result['time_taken']:.3f} s")
            print(f"Throughput: {result['throughput']:.2f} tests/s")
    
    # Assert performance requirements
    for strategy, strategy_results in results.items():
        for result in strategy_results:
            if strategy == "least_connections":
                assert result["time_taken"] < 5  # Should handle connections quickly
            elif strategy == "response_time":
                assert result["time_taken"] < 2  # Should process response times efficiently
            elif strategy == "predictive":
                assert result["time_taken"] < 3  # Should handle load predictions efficiently

@pytest.mark.benchmark
def test_mixed_strategy_workloads(benchmark_load_balancer, large_node_set):
    """Test performance with mixed strategy workloads."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Define mixed workload patterns
    mixed_workloads = [
        {
            "name": "burst_connections",
            "pattern": [
                {"strategy": "least_connections", "duration": 0.1, "count": 1000},
                {"strategy": "response_time", "response_time": 0.2, "count": 500},
                {"strategy": "predictive", "load_pattern": "spike", "count": 200}
            ]
        },
        {
            "name": "gradual_load",
            "pattern": [
                {"strategy": "predictive", "load_pattern": "linear", "count": 500},
                {"strategy": "least_connections", "duration": 0.5, "count": 300},
                {"strategy": "response_time", "response_time": 0.3, "count": 400}
            ]
        },
        {
            "name": "periodic_mixed",
            "pattern": [
                {"strategy": "predictive", "load_pattern": "periodic", "count": 300},
                {"strategy": "least_connections", "duration": 0.2, "count": 600},
                {"strategy": "response_time", "response_time": 0.4, "count": 300}
            ]
        }
    ]
    
    results = {}
    for workload in mixed_workloads:
        start_time = time.time()
        workload_results = []
        
        for step in workload["pattern"]:
            benchmark_load_balancer.strategy = step["strategy"]
            step_start = time.time()
            
            if step["strategy"] == "least_connections":
                for _ in range(step["count"]):
                    node_id = benchmark_load_balancer.select_node()
                    if node_id:
                        node = benchmark_load_balancer.nodes[node_id]
                        node.active_connections += 1
                        time.sleep(step["duration"])
                        node.active_connections -= 1
            
            elif step["strategy"] == "response_time":
                for _ in range(step["count"]):
                    node_id = benchmark_load_balancer.select_node()
                    if node_id:
                        response_time = np.random.normal(step["response_time"], 0.05)
                        benchmark_load_balancer.update_node_load(
                            node_id,
                            {"response_time": max(0.01, response_time)}
                        )
            
            elif step["strategy"] == "predictive":
                for _ in range(step["count"]):
                    node_id = benchmark_load_balancer.select_node()
                    if node_id:
                        if step["load_pattern"] == "linear":
                            load = 0.1 + 0.8 * (_ / step["count"])
                        elif step["load_pattern"] == "spike":
                            load = 0.2 if _ % 10 != 0 else 0.8
                        else:  # periodic
                            load = 0.1 + 0.6 * (np.sin(_ / 10) + 1) / 2
                        
                        benchmark_load_balancer.update_node_load(
                            node_id,
                            {"current_load": load}
                        )
            
            step_end = time.time()
            workload_results.append({
                "strategy": step["strategy"],
                "time_taken": step_end - step_start,
                "throughput": step["count"] / (step_end - step_start)
            })
        
        end_time = time.time()
        results[workload["name"]] = {
            "total_time": end_time - start_time,
            "steps": workload_results
        }
    
    # Log results
    print("\nMixed Strategy Workload Results:")
    for workload_name, result in results.items():
        print(f"\n{workload_name.upper()}:")
        print(f"Total time: {result['total_time']:.3f} s")
        for step in result["steps"]:
            print(f"Strategy: {step['strategy']}")
            print(f"Time taken: {step['time_taken']:.3f} s")
            print(f"Throughput: {step['throughput']:.2f} tests/s")
    
    # Assert performance requirements
    for result in results.values():
        assert result["total_time"] < 10  # Should complete within 10 seconds
        for step in result["steps"]:
            assert step["time_taken"] < 5  # Each step should complete within 5 seconds

@pytest.mark.benchmark
def test_strategy_transitions(benchmark_load_balancer, large_node_set):
    """Benchmark performance of strategy transitions."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Define transition scenarios
    transitions = [
        {
            "name": "round_robin_to_least_connections",
            "from_strategy": "weighted_round_robin",
            "to_strategy": "least_connections",
            "workload": {"duration": 0.1, "connections": 5, "count": 100}
        },
        {
            "name": "least_connections_to_response_time",
            "from_strategy": "least_connections",
            "to_strategy": "response_time",
            "workload": {"response_time": 0.2, "variance": 0.05, "count": 100}
        },
        {
            "name": "response_time_to_predictive",
            "from_strategy": "response_time",
            "to_strategy": "predictive",
            "workload": {"load_pattern": "linear", "start": 0.1, "end": 0.9, "count": 100}
        },
        {
            "name": "predictive_to_round_robin",
            "from_strategy": "predictive",
            "to_strategy": "weighted_round_robin",
            "workload": {"duration": 0.1, "count": 100}
        }
    ]
    
    results = {}
    for transition in transitions:
        # Set initial strategy
        benchmark_load_balancer.strategy = transition["from_strategy"]
        
        # Run initial workload
        initial_metrics = []
        for _ in range(transition["workload"]["count"]):
            if transition["from_strategy"] == "least_connections":
                node_id = benchmark_load_balancer.select_node()
                if node_id:
                    node = benchmark_load_balancer.nodes[node_id]
                    node.active_connections += transition["workload"]["connections"]
                    time.sleep(transition["workload"]["duration"])
                    node.active_connections -= transition["workload"]["connections"]
            elif transition["from_strategy"] == "response_time":
                node_id = benchmark_load_balancer.select_node()
                if node_id:
                    response_time = np.random.normal(
                        transition["workload"]["response_time"],
                        transition["workload"]["variance"]
                    )
                    benchmark_load_balancer.update_node_load(
                        node_id,
                        {"response_time": max(0.01, response_time)}
                    )
            elif transition["from_strategy"] == "predictive":
                node_id = benchmark_load_balancer.select_node()
                if node_id:
                    load = transition["workload"]["start"] + (
                        transition["workload"]["end"] - transition["workload"]["start"]
                    ) * (_ / transition["workload"]["count"])
                    benchmark_load_balancer.update_node_load(
                        node_id,
                        {"current_load": load}
                    )
            else:  # weighted_round_robin
                benchmark_load_balancer.select_node()
            
            initial_metrics.append(benchmark_load_balancer.get_detailed_metrics())
        
        # Measure transition time
        transition_start = time.time()
        benchmark_load_balancer.strategy = transition["to_strategy"]
        transition_time = time.time() - transition_start
        
        # Run workload with new strategy
        post_transition_metrics = []
        for _ in range(transition["workload"]["count"]):
            if transition["to_strategy"] == "least_connections":
                node_id = benchmark_load_balancer.select_node()
                if node_id:
                    node = benchmark_load_balancer.nodes[node_id]
                    node.active_connections += transition["workload"]["connections"]
                    time.sleep(transition["workload"]["duration"])
                    node.active_connections -= transition["workload"]["connections"]
            elif transition["to_strategy"] == "response_time":
                node_id = benchmark_load_balancer.select_node()
                if node_id:
                    response_time = np.random.normal(
                        transition["workload"]["response_time"],
                        transition["workload"]["variance"]
                    )
                    benchmark_load_balancer.update_node_load(
                        node_id,
                        {"response_time": max(0.01, response_time)}
                    )
            elif transition["to_strategy"] == "predictive":
                node_id = benchmark_load_balancer.select_node()
                if node_id:
                    load = transition["workload"]["start"] + (
                        transition["workload"]["end"] - transition["workload"]["start"]
                    ) * (_ / transition["workload"]["count"])
                    benchmark_load_balancer.update_node_load(
                        node_id,
                        {"current_load": load}
                    )
            else:  # weighted_round_robin
                benchmark_load_balancer.select_node()
            
            post_transition_metrics.append(benchmark_load_balancer.get_detailed_metrics())
        
        # Calculate performance metrics
        initial_performance = {
            "avg_selection_time": statistics.mean([
                m["strategy"]["avg_selection_time"]
                for m in initial_metrics
                if m["strategy"]
            ]),
            "success_rate": statistics.mean([
                m["strategy"]["success_rate"]
                for m in initial_metrics
                if m["strategy"]
            ]),
            "load_balance_score": statistics.mean([
                m["strategy"]["load_balance_score"]
                for m in initial_metrics
                if m["strategy"]
            ])
        }
        
        post_transition_performance = {
            "avg_selection_time": statistics.mean([
                m["strategy"]["avg_selection_time"]
                for m in post_transition_metrics
                if m["strategy"]
            ]),
            "success_rate": statistics.mean([
                m["strategy"]["success_rate"]
                for m in post_transition_metrics
                if m["strategy"]
            ]),
            "load_balance_score": statistics.mean([
                m["strategy"]["load_balance_score"]
                for m in post_transition_metrics
                if m["strategy"]
            ])
        }
        
        results[transition["name"]] = {
            "transition_time": transition_time,
            "initial_performance": initial_performance,
            "post_transition_performance": post_transition_performance,
            "performance_change": {
                "selection_time_change": (
                    post_transition_performance["avg_selection_time"] -
                    initial_performance["avg_selection_time"]
                ) / initial_performance["avg_selection_time"] * 100,
                "success_rate_change": (
                    post_transition_performance["success_rate"] -
                    initial_performance["success_rate"]
                ) / initial_performance["success_rate"] * 100,
                "load_balance_change": (
                    post_transition_performance["load_balance_score"] -
                    initial_performance["load_balance_score"]
                ) / initial_performance["load_balance_score"] * 100
            }
        }
    
    # Log results
    print("\nStrategy Transition Results:")
    for transition_name, result in results.items():
        print(f"\n{transition_name.upper()}:")
        print(f"Transition time: {result['transition_time'] * 1000:.3f} ms")
        print("\nInitial Performance:")
        print(f"Average selection time: {result['initial_performance']['avg_selection_time'] * 1000:.3f} ms")
        print(f"Success rate: {result['initial_performance']['success_rate'] * 100:.2f}%")
        print(f"Load balance score: {result['initial_performance']['load_balance_score'] * 100:.2f}%")
        print("\nPost-Transition Performance:")
        print(f"Average selection time: {result['post_transition_performance']['avg_selection_time'] * 1000:.3f} ms")
        print(f"Success rate: {result['post_transition_performance']['success_rate'] * 100:.2f}%")
        print(f"Load balance score: {result['post_transition_performance']['load_balance_score'] * 100:.2f}%")
        print("\nPerformance Change:")
        print(f"Selection time change: {result['performance_change']['selection_time_change']:+.2f}%")
        print(f"Success rate change: {result['performance_change']['success_rate_change']:+.2f}%")
        print(f"Load balance change: {result['performance_change']['load_balance_change']:+.2f}%")
    
    # Assert performance requirements
    for result in results.values():
        assert result["transition_time"] < 0.1  # Should transition in less than 100ms
        assert result["performance_change"]["selection_time_change"] < 50  # Should not increase selection time by more than 50%
        assert result["performance_change"]["success_rate_change"] > -10  # Should not decrease success rate by more than 10%
        assert result["performance_change"]["load_balance_change"] > -20  # Should not decrease load balance by more than 20%

@pytest.mark.benchmark
def test_transition_stability(benchmark_load_balancer, large_node_set):
    """Test stability during frequent strategy transitions."""
    # Add nodes
    for node_id, capabilities in large_node_set.items():
        benchmark_load_balancer.add_node(node_id, capabilities)
    
    # Define transition sequence
    strategies = ["weighted_round_robin", "least_connections", "response_time", "predictive"]
    transitions = 100
    results = []
    
    for i in range(transitions):
        # Select next strategy
        current_strategy = strategies[i % len(strategies)]
        benchmark_load_balancer.strategy = current_strategy
        
        # Run workload
        start_time = time.time()
        for _ in range(10):  # Run 10 operations per transition
            node_id = benchmark_load_balancer.select_node()
            if node_id:
                # Simulate different types of operations
                if current_strategy == "least_connections":
                    node = benchmark_load_balancer.nodes[node_id]
                    node.active_connections += 1
                    time.sleep(0.01)
                    node.active_connections -= 1
                elif current_strategy == "response_time":
                    response_time = np.random.normal(0.2, 0.05)
                    benchmark_load_balancer.update_node_load(
                        node_id,
                        {"response_time": max(0.01, response_time)}
                    )
                elif current_strategy == "predictive":
                    load = 0.1 + 0.8 * (i % 10) / 10
                    benchmark_load_balancer.update_node_load(
                        node_id,
                        {"current_load": load}
                    )
        
        end_time = time.time()
        metrics = benchmark_load_balancer.get_detailed_metrics()
        
        results.append({
            "transition": i + 1,
            "strategy": current_strategy,
            "time_taken": end_time - start_time,
            "metrics": metrics
        })
    
    # Calculate stability metrics
    stability_metrics = {
        "avg_transition_time": statistics.mean([r["time_taken"] for r in results]),
        "std_transition_time": statistics.stdev([r["time_taken"] for r in results]),
        "success_rates": [r["metrics"]["strategy"]["success_rate"] for r in results if r["metrics"]["strategy"]],
        "load_balance_scores": [r["metrics"]["strategy"]["load_balance_score"] for r in results if r["metrics"]["strategy"]]
    }
    
    # Log results
    print("\nTransition Stability Results:")
    print(f"Average transition time: {stability_metrics['avg_transition_time'] * 1000:.3f} ms")
    print(f"Standard deviation of transition time: {stability_metrics['std_transition_time'] * 1000:.3f} ms")
    print(f"Average success rate: {statistics.mean(stability_metrics['success_rates']) * 100:.2f}%")
    print(f"Average load balance score: {statistics.mean(stability_metrics['load_balance_scores']) * 100:.2f}%")
    
    # Assert stability requirements
    assert stability_metrics["avg_transition_time"] < 0.1  # Should average less than 100ms per transition
    assert stability_metrics["std_transition_time"] < 0.05  # Should have low variance in transition times
    assert statistics.mean(stability_metrics["success_rates"]) > 0.9  # Should maintain high success rate
    assert statistics.mean(stability_metrics["load_balance_scores"]) > 0.8  # Should maintain good load balance

@pytest.mark.benchmark
@pytest.mark.edge_cases
async def test_extreme_workload_patterns(benchmark_load_balancer, large_node_set):
    """Test load balancer with extreme workload patterns.
    
    This test evaluates the load balancer's behavior under extreme conditions:
    - Sudden massive spikes in load
    - Complete node failures
    - Resource exhaustion scenarios
    - Network partition simulations
    - Cascading failure scenarios
    """
    # Initialize nodes with varying capabilities
    nodes = [
        Node(f"node-{i}", {"cpu": 4, "memory": 16, "network": 1000})
        for i in range(10)
    ]
    
    for node in nodes:
        benchmark_load_balancer.add_node(node)
    
    # Test massive load spikes
    spike_patterns = [
        # Sudden 10x increase in load
        lambda t: 0.1 if t < 5 else 1.0,
        # Exponential growth
        lambda t: min(0.1 * (2 ** t), 1.0),
        # Step function with multiple spikes
        lambda t: 0.1 if t < 3 else (0.9 if t < 6 else 0.1)
    ]
    
    spike_results = []
    for pattern in spike_patterns:
        start_time = time.time()
        for t in range(10):
            for node in nodes:
                load = pattern(t)
                benchmark_load_balancer.update_node_load(
                    node.id,
                    NodeLoad(
                        cpu_usage=load,
                        memory_usage=load,
                        network_usage=load,
                        active_connections=int(load * 1000)
                    )
                )
            await asyncio.sleep(0.1)
        spike_results.append(time.time() - start_time)
    
    # Test complete node failures
    failure_patterns = [
        # Single node failure
        lambda t: [nodes[0]] if t == 5 else [],
        # Multiple node failures
        lambda t: nodes[:3] if t == 5 else [],
        # Cascading failures
        lambda t: nodes[:t] if t > 5 else []
    ]
    
    failure_results = []
    for pattern in failure_patterns:
        start_time = time.time()
        for t in range(10):
            failed_nodes = pattern(t)
            for node in failed_nodes:
                benchmark_load_balancer.remove_node(node.id)
            await asyncio.sleep(0.1)
        failure_results.append(time.time() - start_time)
    
    # Test resource exhaustion
    exhaustion_patterns = [
        # CPU exhaustion
        lambda t: NodeLoad(cpu_usage=1.0, memory_usage=0.1, network_usage=0.1),
        # Memory exhaustion
        lambda t: NodeLoad(cpu_usage=0.1, memory_usage=1.0, network_usage=0.1),
        # Network exhaustion
        lambda t: NodeLoad(cpu_usage=0.1, memory_usage=0.1, network_usage=1.0)
    ]
    
    exhaustion_results = []
    for pattern in exhaustion_patterns:
        start_time = time.time()
        for t in range(10):
            for node in nodes:
                benchmark_load_balancer.update_node_load(node.id, pattern(t))
            await asyncio.sleep(0.1)
        exhaustion_results.append(time.time() - start_time)
    
    # Test network partition scenarios
    partition_patterns = [
        # Single partition
        lambda t: {nodes[0].id: 1000, nodes[1].id: 100} if t == 5 else {},
        # Multiple partitions
        lambda t: {nodes[i].id: 1000 if i < 5 else 100 for i in range(10)} if t == 5 else {},
        # Dynamic partitions
        lambda t: {nodes[i].id: 1000 if i < t else 100 for i in range(10)}
    ]
    
    partition_results = []
    for pattern in partition_patterns:
        start_time = time.time()
        for t in range(10):
            latencies = pattern(t)
            for node_id, latency in latencies.items():
                benchmark_load_balancer.update_node_load(
                    node_id,
                    NodeLoad(
                        cpu_usage=0.1,
                        memory_usage=0.1,
                        network_usage=0.1,
                        network_latency=latency
                    )
                )
            await asyncio.sleep(0.1)
        partition_results.append(time.time() - start_time)
    
    # Test cascading failure scenarios
    cascade_patterns = [
        # Linear cascade
        lambda t: [nodes[i] for i in range(t)],
        # Exponential cascade
        lambda t: [nodes[i] for i in range(2 ** t) if i < len(nodes)],
        # Random cascade
        lambda t: np.random.choice(nodes, size=min(t, len(nodes)), replace=False)
    ]
    
    cascade_results = []
    for pattern in cascade_patterns:
        start_time = time.time()
        for t in range(10):
            failed_nodes = pattern(t)
            for node in failed_nodes:
                benchmark_load_balancer.remove_node(node.id)
            await asyncio.sleep(0.1)
        cascade_results.append(time.time() - start_time)
    
    # Assertions for each pattern type
    assert all(t < 2.0 for t in spike_results), "Load spike handling too slow"
    assert all(t < 1.0 for t in failure_results), "Failure handling too slow"
    assert all(t < 1.5 for t in exhaustion_results), "Resource exhaustion handling too slow"
    assert all(t < 1.5 for t in partition_results), "Network partition handling too slow"
    assert all(t < 1.0 for t in cascade_results), "Cascade failure handling too slow"
    
    # Verify system stability
    metrics = benchmark_load_balancer.get_detailed_metrics()
    assert metrics["strategy.success_rate"] > 0.8, "Success rate too low after edge cases"
    assert metrics["strategy.load_balance_score"] > 0.7, "Load balance too poor after edge cases"

@pytest.mark.benchmark
@pytest.mark.edge_cases
async def test_resource_contention_scenarios(benchmark_load_balancer, large_node_set):
    """Test load balancer with resource contention scenarios.
    
    This test evaluates the load balancer's behavior under resource contention:
    - CPU contention with varying core counts
    - Memory pressure with different allocation patterns
    - Network bandwidth competition
    - Disk I/O contention
    - Mixed resource contention
    """
    # Initialize nodes with varying resource configurations
    nodes = [
        Node(f"node-{i}", {
            "cpu": 2 if i < 5 else 8,
            "memory": 8 if i < 5 else 32,
            "network": 100 if i < 5 else 1000,
            "disk": "hdd" if i < 5 else "ssd"
        })
        for i in range(10)
    ]
    
    for node in nodes:
        benchmark_load_balancer.add_node(node)
    
    # Test CPU contention patterns
    cpu_patterns = [
        # All cores saturated
        lambda t: {f"cpu_{i}": 1.0 for i in range(8)},
        # Alternating core usage
        lambda t: {f"cpu_{i}": 1.0 if i % 2 == t % 2 else 0.1 for i in range(8)},
        # Bursty core usage
        lambda t: {f"cpu_{i}": 1.0 if t % 3 == 0 else 0.1 for i in range(8)}
    ]
    
    cpu_results = []
    for pattern in cpu_patterns:
        start_time = time.time()
        for t in range(10):
            for node in nodes:
                cpu_usage = pattern(t)
                benchmark_load_balancer.update_node_load(
                    node.id,
                    NodeLoad(
                        cpu_usage=sum(cpu_usage.values()) / len(cpu_usage),
                        cpu_cores_usage=cpu_usage
                    )
                )
            await asyncio.sleep(0.1)
        cpu_results.append(time.time() - start_time)
    
    # Test memory pressure patterns
    memory_patterns = [
        # Linear memory growth
        lambda t: min(0.1 * t, 1.0),
        # Sudden memory spikes
        lambda t: 0.9 if t % 3 == 0 else 0.1,
        # Memory fragmentation simulation
        lambda t: 0.5 + 0.4 * np.sin(t)
    ]
    
    memory_results = []
    for pattern in memory_patterns:
        start_time = time.time()
        for t in range(10):
            for node in nodes:
                memory_usage = pattern(t)
                benchmark_load_balancer.update_node_load(
                    node.id,
                    NodeLoad(
                        memory_usage=memory_usage,
                        memory_fragmentation=0.2 if t % 2 == 0 else 0.8
                    )
                )
            await asyncio.sleep(0.1)
        memory_results.append(time.time() - start_time)
    
    # Test network bandwidth competition
    network_patterns = [
        # Bandwidth saturation
        lambda t: 1.0 if t > 5 else 0.1,
        # Bursty network traffic
        lambda t: 0.9 if t % 2 == 0 else 0.1,
        # Network congestion
        lambda t: min(0.1 * t, 1.0)
    ]
    
    network_results = []
    for pattern in network_patterns:
        start_time = time.time()
        for t in range(10):
            for node in nodes:
                network_usage = pattern(t)
                benchmark_load_balancer.update_node_load(
                    node.id,
                    NodeLoad(
                        network_usage=network_usage,
                        network_latency=100 * network_usage
                    )
                )
            await asyncio.sleep(0.1)
        network_results.append(time.time() - start_time)
    
    # Test disk I/O contention
    disk_patterns = [
        # High disk I/O
        lambda t: {"read": 0.9, "write": 0.9} if t > 5 else {"read": 0.1, "write": 0.1},
        # Read-heavy workload
        lambda t: {"read": 0.9, "write": 0.1} if t % 2 == 0 else {"read": 0.1, "write": 0.1},
        # Write-heavy workload
        lambda t: {"read": 0.1, "write": 0.9} if t % 2 == 0 else {"read": 0.1, "write": 0.1}
    ]
    
    disk_results = []
    for pattern in disk_patterns:
        start_time = time.time()
        for t in range(10):
            for node in nodes:
                disk_usage = pattern(t)
                benchmark_load_balancer.update_node_load(
                    node.id,
                    NodeLoad(
                        disk_read_usage=disk_usage["read"],
                        disk_write_usage=disk_usage["write"]
                    )
                )
            await asyncio.sleep(0.1)
        disk_results.append(time.time() - start_time)
    
    # Test mixed resource contention
    mixed_patterns = [
        # CPU and memory contention
        lambda t: {
            "cpu": 0.9 if t > 5 else 0.1,
            "memory": 0.9 if t > 5 else 0.1,
            "network": 0.1,
            "disk": {"read": 0.1, "write": 0.1}
        },
        # Network and disk contention
        lambda t: {
            "cpu": 0.1,
            "memory": 0.1,
            "network": 0.9 if t % 2 == 0 else 0.1,
            "disk": {"read": 0.9, "write": 0.9} if t % 2 == 0 else {"read": 0.1, "write": 0.1}
        },
        # All resources contention
        lambda t: {
            "cpu": 0.9 if t % 3 == 0 else 0.1,
            "memory": 0.9 if t % 3 == 1 else 0.1,
            "network": 0.9 if t % 3 == 2 else 0.1,
            "disk": {"read": 0.9, "write": 0.9} if t % 2 == 0 else {"read": 0.1, "write": 0.1}
        }
    ]
    
    mixed_results = []
    for pattern in mixed_patterns:
        start_time = time.time()
        for t in range(10):
            for node in nodes:
                usage = pattern(t)
                benchmark_load_balancer.update_node_load(
                    node.id,
                    NodeLoad(
                        cpu_usage=usage["cpu"],
                        memory_usage=usage["memory"],
                        network_usage=usage["network"],
                        disk_read_usage=usage["disk"]["read"],
                        disk_write_usage=usage["disk"]["write"]
                    )
                )
            await asyncio.sleep(0.1)
        mixed_results.append(time.time() - start_time)
    
    # Assertions for each pattern type
    assert all(t < 1.5 for t in cpu_results), "CPU contention handling too slow"
    assert all(t < 1.5 for t in memory_results), "Memory pressure handling too slow"
    assert all(t < 1.5 for t in network_results), "Network contention handling too slow"
    assert all(t < 1.5 for t in disk_results), "Disk I/O handling too slow"
    assert all(t < 2.0 for t in mixed_results), "Mixed resource handling too slow"
    
    # Verify system stability
    metrics = benchmark_load_balancer.get_detailed_metrics()
    assert metrics["strategy.success_rate"] > 0.8, "Success rate too low after resource contention"
    assert metrics["strategy.resource_efficiency"] > 0.7, "Resource efficiency too low after contention"

@pytest.mark.benchmark
@pytest.mark.edge_cases
async def test_complex_mixed_workloads(benchmark_load_balancer, large_node_set):
    """Test load balancer with complex mixed workload patterns.
    
    This test evaluates the load balancer's behavior under complex, realistic workloads:
    - E-commerce traffic patterns (daily cycles, flash sales)
    - Video streaming patterns (prime time, off-peak)
    - IoT device patterns (periodic updates, event bursts)
    - Mixed application patterns (web, API, background jobs)
    """
    # Initialize nodes with varying capabilities
    nodes = [
        Node(f"node-{i}", {
            "cpu": 4 if i < 5 else 8,
            "memory": 16 if i < 5 else 32,
            "network": 1000,
            "disk": "ssd",
            "gpu": "none" if i < 5 else "medium"
        })
        for i in range(10)
    ]
    
    for node in nodes:
        benchmark_load_balancer.add_node(node)
    
    # E-commerce traffic patterns
    ecommerce_patterns = [
        # Daily cycle with flash sale
        lambda t: {
            "base_load": 0.3 + 0.2 * np.sin(t * np.pi / 12),  # Daily cycle
            "flash_sale": 0.8 if 5 <= t < 6 else 0.0,  # Flash sale at hour 5
            "checkout_spike": 0.9 if t % 24 == 0 else 0.0,  # Daily checkout spike
            "search_load": 0.4 + 0.3 * np.random.random()  # Search traffic
        },
        # Weekend vs weekday pattern
        lambda t: {
            "base_load": 0.4 if t % 24 < 8 or t % 24 >= 20 else 0.6,  # Off-peak vs peak
            "weekend_boost": 0.2 if t // 24 % 7 >= 5 else 0.0,  # Weekend boost
            "mobile_traffic": 0.3 + 0.2 * np.sin(t * np.pi / 12),  # Mobile traffic cycle
            "api_calls": 0.5 + 0.3 * np.random.random()  # API traffic
        }
    ]
    
    # Video streaming patterns
    streaming_patterns = [
        # Prime time viewing
        lambda t: {
            "base_load": 0.3 + 0.4 * np.sin(t * np.pi / 12),  # Daily cycle
            "prime_time": 0.8 if 18 <= t % 24 < 22 else 0.0,  # Prime time boost
            "live_events": 0.9 if t % 24 == 20 else 0.0,  # Live event spike
            "cdn_load": 0.6 + 0.2 * np.random.random()  # CDN traffic
        },
        # Content delivery patterns
        lambda t: {
            "base_load": 0.4,
            "new_release": 0.9 if t % 24 == 0 else 0.0,  # New content release
            "recommendation_load": 0.5 + 0.2 * np.sin(t * np.pi / 6),  # Recommendation engine
            "transcoding_load": 0.7 if t % 12 == 0 else 0.3  # Transcoding jobs
        }
    ]
    
    # IoT device patterns
    iot_patterns = [
        # Smart home patterns
        lambda t: {
            "base_load": 0.2,
            "morning_routine": 0.8 if 6 <= t % 24 < 8 else 0.0,  # Morning routine
            "evening_routine": 0.8 if 17 <= t % 24 < 19 else 0.0,  # Evening routine
            "sensor_updates": 0.3 + 0.1 * np.sin(t * np.pi / 6),  # Periodic updates
            "event_bursts": 0.9 if t % 12 == 0 else 0.0  # Event bursts
        },
        # Industrial IoT patterns
        lambda t: {
            "base_load": 0.3,
            "shift_change": 0.7 if t % 8 == 0 else 0.0,  # Shift changes
            "maintenance_windows": 0.9 if t % 24 == 0 else 0.0,  # Maintenance
            "batch_processing": 0.8 if t % 12 == 0 else 0.2,  # Batch jobs
            "real_time_monitoring": 0.4 + 0.2 * np.random.random()  # Monitoring
        }
    ]
    
    # Mixed application patterns
    mixed_patterns = [
        # Web application patterns
        lambda t: {
            "web_traffic": 0.4 + 0.3 * np.sin(t * np.pi / 12),  # Web traffic
            "api_load": 0.5 + 0.2 * np.random.random(),  # API load
            "background_jobs": 0.6 if t % 6 == 0 else 0.2,  # Background jobs
            "database_load": 0.4 + 0.3 * np.sin(t * np.pi / 6),  # Database load
            "cache_hits": 0.7 if t % 3 == 0 else 0.3  # Cache usage
        },
        # Microservices patterns
        lambda t: {
            "frontend": 0.4 + 0.2 * np.sin(t * np.pi / 12),  # Frontend service
            "auth_service": 0.3 + 0.1 * np.random.random(),  # Auth service
            "payment_service": 0.7 if t % 24 == 0 else 0.3,  # Payment service
            "notification_service": 0.5 + 0.2 * np.sin(t * np.pi / 6),  # Notifications
            "analytics_service": 0.6 if t % 12 == 0 else 0.2  # Analytics
        }
    ]
    
    # Test each pattern type
    pattern_results = {}
    for pattern_type, patterns in [
        ("ecommerce", ecommerce_patterns),
        ("streaming", streaming_patterns),
        ("iot", iot_patterns),
        ("mixed", mixed_patterns)
    ]:
        results = []
        for pattern in patterns:
            start_time = time.time()
            for t in range(24):  # Simulate 24 hours
                for node in nodes:
                    load_pattern = pattern(t)
                    # Calculate total load considering all components
                    total_load = max(
                        sum(load_pattern.values()) / len(load_pattern),
                        max(load_pattern.values())
                    )
                    
                    benchmark_load_balancer.update_node_load(
                        node.id,
                        NodeLoad(
                            cpu_usage=total_load * 0.8,
                            memory_usage=total_load * 0.7,
                            network_usage=total_load * 0.9,
                            active_connections=int(total_load * 1000),
                            resource_components=load_pattern
                        )
                    )
                await asyncio.sleep(0.1)
            results.append(time.time() - start_time)
        pattern_results[pattern_type] = results
    
    # Assertions for each pattern type
    for pattern_type, results in pattern_results.items():
        assert all(t < 3.0 for t in results), f"{pattern_type} pattern handling too slow"
    
    # Verify system stability
    metrics = benchmark_load_balancer.get_detailed_metrics()
    assert metrics["strategy.success_rate"] > 0.85, "Success rate too low after complex workloads"
    assert metrics["strategy.load_balance_score"] > 0.75, "Load balance too poor after complex workloads"
    assert metrics["strategy.resource_efficiency"] > 0.7, "Resource efficiency too low after complex workloads"

@pytest.mark.benchmark
@pytest.mark.edge_cases
async def test_workload_transition_scenarios(benchmark_load_balancer, large_node_set):
    """Test load balancer with specific transition scenarios between workload patterns.
    
    This test evaluates the load balancer's behavior during transitions between:
    - E-commerce to streaming (flash sale to live event)
    - IoT to mixed application (device updates to web traffic)
    - Streaming to IoT (prime time to device routines)
    - Mixed application to e-commerce (background jobs to checkout)
    """
    # Initialize nodes with varying capabilities
    nodes = [
        Node(f"node-{i}", {
            "cpu": 4 if i < 5 else 8,
            "memory": 16 if i < 5 else 32,
            "network": 1000,
            "disk": "ssd",
            "gpu": "none" if i < 5 else "medium"
        })
        for i in range(10)
    ]
    
    for node in nodes:
        benchmark_load_balancer.add_node(node)
    
    # Define transition scenarios
    transition_scenarios = [
        {
            "name": "ecommerce_to_streaming",
            "from_pattern": lambda t: {
                "base_load": 0.3 + 0.2 * np.sin(t * np.pi / 12),
                "flash_sale": 0.8 if 5 <= t < 6 else 0.0,
                "checkout_spike": 0.9 if t % 24 == 0 else 0.0,
                "search_load": 0.4 + 0.3 * np.random.random()
            },
            "to_pattern": lambda t: {
                "base_load": 0.3 + 0.4 * np.sin(t * np.pi / 12),
                "prime_time": 0.8 if 18 <= t % 24 < 22 else 0.0,
                "live_events": 0.9 if t % 24 == 20 else 0.0,
                "cdn_load": 0.6 + 0.2 * np.random.random()
            },
            "transition_point": 6,  # Transition at hour 6
            "transition_duration": 1  # 1 hour transition period
        },
        {
            "name": "iot_to_mixed",
            "from_pattern": lambda t: {
                "base_load": 0.2,
                "morning_routine": 0.8 if 6 <= t % 24 < 8 else 0.0,
                "evening_routine": 0.8 if 17 <= t % 24 < 19 else 0.0,
                "sensor_updates": 0.3 + 0.1 * np.sin(t * np.pi / 6),
                "event_bursts": 0.9 if t % 12 == 0 else 0.0
            },
            "to_pattern": lambda t: {
                "web_traffic": 0.4 + 0.3 * np.sin(t * np.pi / 12),
                "api_load": 0.5 + 0.2 * np.random.random(),
                "background_jobs": 0.6 if t % 6 == 0 else 0.2,
                "database_load": 0.4 + 0.3 * np.sin(t * np.pi / 6),
                "cache_hits": 0.7 if t % 3 == 0 else 0.3
            },
            "transition_point": 8,  # Transition at hour 8
            "transition_duration": 2  # 2 hour transition period
        },
        {
            "name": "streaming_to_iot",
            "from_pattern": lambda t: {
                "base_load": 0.3 + 0.4 * np.sin(t * np.pi / 12),
                "prime_time": 0.8 if 18 <= t % 24 < 22 else 0.0,
                "live_events": 0.9 if t % 24 == 20 else 0.0,
                "cdn_load": 0.6 + 0.2 * np.random.random()
            },
            "to_pattern": lambda t: {
                "base_load": 0.3,
                "shift_change": 0.7 if t % 8 == 0 else 0.0,
                "maintenance_windows": 0.9 if t % 24 == 0 else 0.0,
                "batch_processing": 0.8 if t % 12 == 0 else 0.2,
                "real_time_monitoring": 0.4 + 0.2 * np.random.random()
            },
            "transition_point": 22,  # Transition at hour 22
            "transition_duration": 1  # 1 hour transition period
        },
        {
            "name": "mixed_to_ecommerce",
            "from_pattern": lambda t: {
                "frontend": 0.4 + 0.2 * np.sin(t * np.pi / 12),
                "auth_service": 0.3 + 0.1 * np.random.random(),
                "payment_service": 0.7 if t % 24 == 0 else 0.3,
                "notification_service": 0.5 + 0.2 * np.sin(t * np.pi / 6),
                "analytics_service": 0.6 if t % 12 == 0 else 0.2
            },
            "to_pattern": lambda t: {
                "base_load": 0.4 if t % 24 < 8 or t % 24 >= 20 else 0.6,
                "weekend_boost": 0.2 if t // 24 % 7 >= 5 else 0.0,
                "mobile_traffic": 0.3 + 0.2 * np.sin(t * np.pi / 12),
                "api_calls": 0.5 + 0.3 * np.random.random()
            },
            "transition_point": 0,  # Transition at hour 0
            "transition_duration": 2  # 2 hour transition period
        }
    ]
    
    # Test each transition scenario
    transition_results = {}
    for scenario in transition_scenarios:
        results = {
            "workload_metrics": [],
            "resource_metrics": [],
            "strategy_metrics": [],
            "performance_metrics": [],
            "transition_times": [],
            "timestamp": []
        }
        
        start_time = time.time()
        for t in range(24):  # Simulate 24 hours
            # Determine current pattern based on transition point
            if t < scenario["transition_point"]:
                pattern = scenario["from_pattern"]
            elif t >= scenario["transition_point"] + scenario["transition_duration"]:
                pattern = scenario["to_pattern"]
            else:
                # During transition, blend patterns
                transition_progress = (t - scenario["transition_point"]) / scenario["transition_duration"]
                from_pattern = scenario["from_pattern"](t)
                to_pattern = scenario["to_pattern"](t)
                pattern = lambda t: {
                    k: from_pattern[k] * (1 - transition_progress) + to_pattern[k] * transition_progress
                    for k in set(from_pattern.keys()) | set(to_pattern.keys())
                }
            
            # Apply pattern to all nodes
            for node in nodes:
                load_pattern = pattern(t)
                total_load = max(
                    sum(load_pattern.values()) / len(load_pattern),
                    max(load_pattern.values())
                )
                
                benchmark_load_balancer.update_node_load(
                    node.id,
                    NodeLoad(
                        cpu_usage=total_load * 0.8,
                        memory_usage=total_load * 0.7,
                        network_usage=total_load * 0.9,
                        active_connections=int(total_load * 1000),
                        resource_components=load_pattern
                    )
                )
            
            # Record metrics at different stages
            metrics = benchmark_load_balancer.get_detailed_metrics()
            if t < scenario["transition_point"]:
                results["pre_transition_metrics"].append(metrics)
            elif t >= scenario["transition_point"] + scenario["transition_duration"]:
                results["post_transition_metrics"].append(metrics)
            else:
                results["transition_metrics"].append(metrics)
                results["transition_times"].append(time.time() - start_time)
            
            await asyncio.sleep(0.1)
        
        transition_results[scenario["name"]] = results
    
    # Analyze transition performance
    for scenario_name, results in transition_results.items():
        # Calculate transition metrics
        pre_avg_success = np.mean([m["strategy.success_rate"] for m in results["pre_transition_metrics"]])
        transition_avg_success = np.mean([m["strategy.success_rate"] for m in results["transition_metrics"]])
        post_avg_success = np.mean([m["strategy.success_rate"] for m in results["post_transition_metrics"]])
        
        # Calculate transition times
        avg_transition_time = np.mean(results["transition_times"])
        max_transition_time = np.max(results["transition_times"])
        
        # Assert transition requirements
        assert transition_avg_success > 0.8, f"{scenario_name} transition success rate too low"
        assert avg_transition_time < 1.0, f"{scenario_name} average transition time too high"
        assert max_transition_time < 2.0, f"{scenario_name} maximum transition time too high"
        assert abs(post_avg_success - pre_avg_success) < 0.1, f"{scenario_name} success rate degradation too high"
    
    # Verify overall system stability
    metrics = benchmark_load_balancer.get_detailed_metrics()
    assert metrics["strategy.success_rate"] > 0.85, "Success rate too low after transitions"
    assert metrics["strategy.load_balance_score"] > 0.75, "Load balance too poor after transitions"
    assert metrics["strategy.resource_efficiency"] > 0.7, "Resource efficiency too low after transitions"

@pytest.mark.benchmark
@pytest.mark.edge_cases
async def test_advanced_transition_analysis(benchmark_load_balancer, large_node_set):
    """Test load balancer with advanced statistical analysis of transition patterns.
    
    This test evaluates the load balancer's behavior using advanced statistical methods:
    - Time series analysis (trend, seasonality, stationarity)
    - Correlation analysis between metrics
    - Distribution analysis of performance metrics
    - Anomaly detection during transitions
    - Statistical significance testing
    """
    # Initialize nodes with varying capabilities
    nodes = [
        Node(f"node-{i}", {
            "cpu": 4 if i < 5 else 8,
            "memory": 16 if i < 5 else 32,
            "network": 1000,
            "disk": "ssd",
            "gpu": "none" if i < 5 else "medium"
        })
        for i in range(10)
    ]
    
    for node in nodes:
        benchmark_load_balancer.add_node(node)
    
    # Define test scenarios with different transition characteristics
    test_scenarios = [
        {
            "name": "gradual_transition",
            "pattern": lambda t: {
                "load": 0.3 + 0.5 * (1 - np.exp(-t/10)),  # Gradual exponential increase
                "variability": 0.1 * np.sin(t * np.pi / 6)  # Periodic variation
            },
            "duration": 24
        },
        {
            "name": "step_transition",
            "pattern": lambda t: {
                "load": 0.3 if t < 12 else 0.8,  # Sudden step change
                "variability": 0.1 if t < 12 else 0.2  # Increased variability
            },
            "duration": 24
        },
        {
            "name": "oscillating_transition",
            "pattern": lambda t: {
                "load": 0.5 + 0.3 * np.sin(t * np.pi / 6),  # Oscillating load
                "variability": 0.1 + 0.05 * np.sin(t * np.pi / 3)  # Varying variability
            },
            "duration": 24
        }
    ]
    
    # Run tests and collect metrics
    analysis_results = {}
    for scenario in test_scenarios:
        metrics = {
            "load": [],
            "success_rate": [],
            "response_time": [],
            "resource_utilization": [],
            "error_rate": [],
            "timestamp": []
        }
        
        start_time = time.time()
        for t in range(scenario["duration"]):
            pattern = scenario["pattern"](t)
            
            # Apply pattern to all nodes
            for node in nodes:
                benchmark_load_balancer.update_node_load(
                    node.id,
                    NodeLoad(
                        cpu_usage=pattern["load"] * 0.8,
                        memory_usage=pattern["load"] * 0.7,
                        network_usage=pattern["load"] * 0.9,
                        active_connections=int(pattern["load"] * 1000),
                        resource_components={"variability": pattern["variability"]}
                    )
                )
            
            # Collect metrics
            current_metrics = benchmark_load_balancer.get_detailed_metrics()
            metrics["load"].append(pattern["load"])
            metrics["success_rate"].append(current_metrics["strategy.success_rate"])
            metrics["response_time"].append(current_metrics["strategy.avg_selection_time"])
            metrics["resource_utilization"].append(current_metrics["strategy.resource_efficiency"])
            metrics["error_rate"].append(1 - current_metrics["strategy.success_rate"])
            metrics["timestamp"].append(time.time() - start_time)
            
            await asyncio.sleep(0.1)
        
        # Perform statistical analysis
        analysis = {
            "time_series": {},
            "correlation": {},
            "distribution": {},
            "anomalies": {},
            "significance": {}
        }
        
        # Time series analysis
        for metric in ["load", "success_rate", "response_time", "resource_utilization", "error_rate"]:
            values = np.array(metrics[metric])
            timestamps = np.array(metrics["timestamp"])
            
            # Trend analysis
            slope, intercept = np.polyfit(timestamps, values, 1)
            analysis["time_series"][f"{metric}_trend"] = {
                "slope": slope,
                "intercept": intercept,
                "r_squared": np.corrcoef(timestamps, values)[0, 1] ** 2
            }
            
            # Seasonality analysis
            if len(values) >= 12:  # Need enough points for seasonality
                seasonal_decomposition = seasonal_decompose(
                    pd.Series(values, index=pd.date_range(start='1/1/2020', periods=len(values), freq='H')),
                    model='additive',
                    period=12
                )
                analysis["time_series"][f"{metric}_seasonality"] = {
                    "trend": seasonal_decomposition.trend.tolist(),
                    "seasonal": seasonal_decomposition.seasonal.tolist(),
                    "residual": seasonal_decomposition.resid.tolist()
                }
            
            # Stationarity test
            adf_result = adfuller(values)
            analysis["time_series"][f"{metric}_stationarity"] = {
                "adf_statistic": adf_result[0],
                "p_value": adf_result[1],
                "is_stationary": adf_result[1] < 0.05
            }
        
        # Correlation analysis
        metric_pairs = [
            ("load", "success_rate"),
            ("load", "response_time"),
            ("load", "resource_utilization"),
            ("success_rate", "error_rate")
        ]
        for metric1, metric2 in metric_pairs:
            correlation = np.corrcoef(metrics[metric1], metrics[metric2])[0, 1]
            analysis["correlation"][f"{metric1}_{metric2}"] = {
                "pearson": correlation,
                "spearman": spearmanr(metrics[metric1], metrics[metric2])[0],
                "kendall": kendalltau(metrics[metric1], metrics[metric2])[0]
            }
        
        # Distribution analysis
        for metric in ["success_rate", "response_time", "resource_utilization"]:
            values = np.array(metrics[metric])
            analysis["distribution"][metric] = {
                "mean": np.mean(values),
                "median": np.median(values),
                "std": np.std(values),
                "skew": skew(values),
                "kurtosis": kurtosis(values),
                "shapiro_p": shapiro(values)[1],
                "is_normal": shapiro(values)[1] > 0.05
            }
        
        # Anomaly detection
        for metric in ["success_rate", "response_time", "resource_utilization"]:
            values = np.array(metrics[metric])
            z_scores = np.abs(stats.zscore(values))
            anomalies = np.where(z_scores > 3)[0]
            analysis["anomalies"][metric] = {
                "count": len(anomalies),
                "indices": anomalies.tolist(),
                "values": values[anomalies].tolist() if len(anomalies) > 0 else [],
                "severity": z_scores[anomalies].tolist() if len(anomalies) > 0 else []
            }
        
        # Statistical significance testing
        transition_point = scenario["duration"] // 2
        for metric in ["success_rate", "response_time", "resource_utilization"]:
            pre_values = np.array(metrics[metric][:transition_point])
            post_values = np.array(metrics[metric][transition_point:])
            
            # t-test for means
            t_stat, p_value = ttest_ind(pre_values, post_values)
            analysis["significance"][metric] = {
                "t_test": {
                    "statistic": t_stat,
                    "p_value": p_value,
                    "significant": p_value < 0.05
                },
                "mann_whitney": {
                    "statistic": mannwhitneyu(pre_values, post_values)[0],
                    "p_value": mannwhitneyu(pre_values, post_values)[1],
                    "significant": mannwhitneyu(pre_values, post_values)[1] < 0.05
                }
            }
        
        analysis_results[scenario["name"]] = analysis
    
    # Assertions based on statistical analysis
    for scenario_name, analysis in analysis_results.items():
        # Check stationarity
        for metric in ["success_rate", "response_time", "resource_utilization"]:
            assert analysis["time_series"][f"{metric}_stationarity"]["is_stationary"], \
                f"{scenario_name}: {metric} is not stationary"
        
        # Check correlation strength
        assert abs(analysis["correlation"]["load_success_rate"]["pearson"]) > 0.3, \
            f"{scenario_name}: Weak correlation between load and success rate"
        
        # Check distribution normality
        for metric in ["success_rate", "response_time"]:
            assert analysis["distribution"][metric]["is_normal"], \
                f"{scenario_name}: {metric} distribution is not normal"
        
        # Check anomaly frequency
        for metric in ["success_rate", "response_time"]:
            assert analysis["anomalies"][metric]["count"] < len(metrics[metric]) * 0.05, \
                f"{scenario_name}: Too many anomalies in {metric}"
        
        # Check significance of changes
        for metric in ["success_rate", "response_time"]:
            assert not analysis["significance"][metric]["t_test"]["significant"], \
                f"{scenario_name}: Significant change in {metric} mean"
            assert not analysis["significance"][metric]["mann_whitney"]["significant"], \
                f"{scenario_name}: Significant change in {metric} distribution"
    
    # Verify overall system stability
    metrics = benchmark_load_balancer.get_detailed_metrics()
    assert metrics["strategy.success_rate"] > 0.85, "Success rate too low after statistical analysis"
    assert metrics["strategy.load_balance_score"] > 0.75, "Load balance too poor after statistical analysis"
    assert metrics["strategy.resource_efficiency"] > 0.7, "Resource efficiency too low after statistical analysis" 

@pytest.mark.benchmark
@pytest.mark.edge_cases
async def test_resource_edge_cases(benchmark_load_balancer, large_node_set):
    """Test load balancer with resource-specific edge cases during transitions.
    
    This test evaluates the load balancer's behavior under extreme resource conditions:
    - CPU saturation and throttling
    - Memory pressure and swapping
    - Network congestion and latency spikes
    - Disk I/O bottlenecks
    - Mixed resource exhaustion
    """
    # Initialize nodes with varying resource configurations
    nodes = [
        Node(f"node-{i}", {
            "cpu": 2 if i < 3 else (4 if i < 6 else 8),
            "memory": 4 if i < 3 else (8 if i < 6 else 16),
            "network": 100 if i < 3 else (500 if i < 6 else 1000),
            "disk": "hdd" if i < 3 else "ssd",
            "gpu": "none" if i < 6 else "medium"
        })
        for i in range(10)
    ]
    
    for node in nodes:
        benchmark_load_balancer.add_node(node)
    
    # Initialize visualizer
    visualizer = ResourceVisualizer()
    
    # Define resource edge cases
    edge_cases = [
        {
            "name": "cpu_saturation",
            "pattern": lambda t: {
                "cpu_usage": min(1.0, 0.3 + 0.7 * (1 - np.exp(-t/5))),  # Rapid CPU saturation
                "cpu_throttling": 0.8 if t > 10 else 0.0,  # CPU throttling after saturation
                "thermal_throttling": 0.9 if t > 15 else 0.0,  # Thermal throttling
                "core_imbalance": {f"core_{i}": 1.0 if i % 2 == 0 else 0.1 for i in range(8)}  # Uneven core usage
            },
            "transition_point": 10,
            "recovery_point": 20
        },
        {
            "name": "memory_pressure",
            "pattern": lambda t: {
                "memory_usage": min(1.0, 0.2 + 0.8 * (1 - np.exp(-t/5))),  # Rapid memory fill
                "swap_usage": max(0.0, 0.5 * (t - 8) / 5 if t > 8 else 0.0),  # Swap usage
                "memory_fragmentation": 0.7 if t > 12 else 0.1,  # Memory fragmentation
                "oom_risk": 0.9 if t > 15 else 0.0  # Out of memory risk
            },
            "transition_point": 8,
            "recovery_point": 18
        },
        {
            "name": "network_congestion",
            "pattern": lambda t: {
                "network_usage": min(1.0, 0.3 + 0.7 * (1 - np.exp(-t/5))),  # Network saturation
                "latency": 100 * (1 + np.sin(t * np.pi / 3)),  # Latency spikes
                "packet_loss": 0.1 if t > 10 else 0.0,  # Packet loss
                "bandwidth_throttling": 0.8 if t > 12 else 0.0  # Bandwidth throttling
            },
            "transition_point": 10,
            "recovery_point": 20
        },
        {
            "name": "disk_io_bottleneck",
            "pattern": lambda t: {
                "disk_usage": min(1.0, 0.3 + 0.7 * (1 - np.exp(-t/5))),  # Disk saturation
                "read_latency": 50 * (1 + np.sin(t * np.pi / 4)),  # Read latency
                "write_latency": 70 * (1 + np.sin(t * np.pi / 4)),  # Write latency
                "io_queue_depth": 32 if t > 10 else 8  # IO queue depth
            },
            "transition_point": 10,
            "recovery_point": 20
        },
        {
            "name": "mixed_resource_exhaustion",
            "pattern": lambda t: {
                "cpu_usage": min(1.0, 0.3 + 0.7 * (1 - np.exp(-t/5))),
                "memory_usage": min(1.0, 0.2 + 0.8 * (1 - np.exp(-t/5))),
                "network_usage": min(1.0, 0.3 + 0.7 * (1 - np.exp(-t/5))),
                "disk_usage": min(1.0, 0.3 + 0.7 * (1 - np.exp(-t/5))),
                "resource_contention": 0.8 if t > 10 else 0.0
            },
            "transition_point": 10,
            "recovery_point": 20
        }
    ]
    
    # Test each edge case
    edge_case_results = {}
    for case in edge_cases:
        metrics = {
            "resource_usage": [],
            "performance_metrics": [],
            "error_rates": [],
            "recovery_times": [],
            "timestamp": []
        }
        
        start_time = time.time()
        for t in range(24):  # Simulate 24 time units
            pattern = case["pattern"](t)
            
            # Apply pattern to all nodes
            for node in nodes:
                # Calculate node-specific resource limits
                cpu_limit = node.capabilities["cpu"] / 8  # Normalize to 0-1
                memory_limit = node.capabilities["memory"] / 16  # Normalize to 0-1
                network_limit = node.capabilities["network"] / 1000  # Normalize to 0-1
                
                # Apply resource-specific patterns
                resource_load = NodeLoad(
                    cpu_usage=min(pattern.get("cpu_usage", 0) * cpu_limit, 1.0),
                    memory_usage=min(pattern.get("memory_usage", 0) * memory_limit, 1.0),
                    network_usage=min(pattern.get("network_usage", 0) * network_limit, 1.0),
                    disk_usage=pattern.get("disk_usage", 0),
                    active_connections=int(pattern.get("network_usage", 0) * 1000),
                    resource_components={
                        "cpu_throttling": pattern.get("cpu_throttling", 0),
                        "thermal_throttling": pattern.get("thermal_throttling", 0),
                        "core_imbalance": pattern.get("core_imbalance", {}),
                        "swap_usage": pattern.get("swap_usage", 0),
                        "memory_fragmentation": pattern.get("memory_fragmentation", 0),
                        "oom_risk": pattern.get("oom_risk", 0),
                        "latency": pattern.get("latency", 0),
                        "packet_loss": pattern.get("packet_loss", 0),
                        "bandwidth_throttling": pattern.get("bandwidth_throttling", 0),
                        "read_latency": pattern.get("read_latency", 0),
                        "write_latency": pattern.get("write_latency", 0),
                        "io_queue_depth": pattern.get("io_queue_depth", 8),
                        "resource_contention": pattern.get("resource_contention", 0)
                    }
                )
                
                benchmark_load_balancer.update_node_load(node.id, resource_load)
            
            # Collect metrics
            current_metrics = benchmark_load_balancer.get_detailed_metrics()
            metrics["resource_usage"].append(pattern)
            metrics["performance_metrics"].append(current_metrics)
            metrics["error_rates"].append(1 - current_metrics["strategy.success_rate"])
            metrics["timestamp"].append(time.time() - start_time)
            
            # Track recovery times
            if t == case["transition_point"]:
                transition_time = time.time()
            elif t == case["recovery_point"]:
                recovery_time = time.time() - transition_time
                metrics["recovery_times"].append(recovery_time)
            
            await asyncio.sleep(0.1)
        
        edge_case_results[case["name"]] = metrics
        
        # Generate visualizations for this edge case
        visualizer.save_visualizations(metrics, f"visualizations/{case['name']}")
    
    # Analyze results and make assertions
    for case_name, results in edge_case_results.items():
        # Check resource usage patterns
        resource_usage = np.array([r["cpu_usage"] for r in results["resource_usage"]])
        assert np.max(resource_usage) <= 1.0, f"{case_name}: CPU usage exceeded 100%"
        
        # Check performance degradation
        pre_transition_metrics = results["performance_metrics"][:case["transition_point"]]
        during_transition_metrics = results["performance_metrics"][case["transition_point"]:case["recovery_point"]]
        post_transition_metrics = results["performance_metrics"][case["recovery_point"]:]
        
        pre_success_rate = np.mean([m["strategy.success_rate"] for m in pre_transition_metrics])
        during_success_rate = np.mean([m["strategy.success_rate"] for m in during_transition_metrics])
        post_success_rate = np.mean([m["strategy.success_rate"] for m in post_transition_metrics])
        
        # Assert performance requirements
        assert during_success_rate > 0.7, f"{case_name}: Success rate too low during transition"
        assert post_success_rate > 0.8, f"{case_name}: Success rate too low after recovery"
        assert abs(post_success_rate - pre_success_rate) < 0.1, f"{case_name}: Success rate degradation too high"
        
        # Check recovery times
        if results["recovery_times"]:
            recovery_time = results["recovery_times"][0]
            assert recovery_time < 5.0, f"{case_name}: Recovery time too long"
    
    # Verify overall system stability
    metrics = benchmark_load_balancer.get_detailed_metrics()
    assert metrics["strategy.success_rate"] > 0.8, "Success rate too low after edge cases"
    assert metrics["strategy.load_balance_score"] > 0.7, "Load balance too poor after edge cases"
    assert metrics["strategy.resource_efficiency"] > 0.6, "Resource efficiency too low after edge cases"

@pytest.mark.benchmark
@pytest.mark.edge_cases
async def test_complex_simultaneous_transitions(benchmark_load_balancer, large_node_set):
    """Test load balancer with complex simultaneous transitions.
    
    This test evaluates the load balancer's behavior during multiple simultaneous transitions:
    - Multiple workload pattern transitions
    - Resource configuration changes
    - Strategy changes
    - Node capacity changes
    """
    # Initialize nodes with varying capabilities
    nodes = [
        Node(f"node-{i}", {
            "cpu": 4 if i < 5 else 8,
            "memory": 16 if i < 5 else 32,
            "network": 1000,
            "disk": "ssd",
            "gpu": "none" if i < 5 else "medium",
            "numa_nodes": 1 if i < 3 else 2,
            "cache_size": "small" if i < 3 else ("medium" if i < 6 else "large")
        })
        for i in range(10)
    ]
    
    for node in nodes:
        benchmark_load_balancer.add_node(node)
    
    # Define complex transition scenarios
    transition_scenarios = [
        {
            "name": "workload_and_resource_transition",
            "workload_transitions": [
                {
                    "from": lambda t: {
                        "base_load": 0.3 + 0.2 * np.sin(t * np.pi / 12),
                        "flash_sale": 0.8 if 5 <= t < 6 else 0.0,
                        "checkout_spike": 0.9 if t % 24 == 0 else 0.0
                    },
                    "to": lambda t: {
                        "base_load": 0.3 + 0.4 * np.sin(t * np.pi / 12),
                        "prime_time": 0.8 if 18 <= t % 24 < 22 else 0.0,
                        "live_events": 0.9 if t % 24 == 20 else 0.0
                    },
                    "start": 6,
                    "duration": 2
                },
                {
                    "from": lambda t: {
                        "api_load": 0.5 + 0.2 * np.random.random(),
                        "background_jobs": 0.6 if t % 6 == 0 else 0.2
                    },
                    "to": lambda t: {
                        "api_load": 0.7 + 0.1 * np.random.random(),
                        "background_jobs": 0.8 if t % 4 == 0 else 0.3
                    },
                    "start": 8,
                    "duration": 2
                }
            ],
            "resource_transitions": [
                {
                    "type": "cpu",
                    "from": lambda t: {"cores": 4, "frequency": 2.4},
                    "to": lambda t: {"cores": 8, "frequency": 3.2},
                    "start": 7,
                    "duration": 1
                },
                {
                    "type": "memory",
                    "from": lambda t: {"size": 16, "speed": 2400},
                    "to": lambda t: {"size": 32, "speed": 3200},
                    "start": 7,
                    "duration": 1
                }
            ],
            "strategy_transitions": [
                {
                    "from": "round_robin",
                    "to": "least_connections",
                    "start": 6,
                    "duration": 1
                },
                {
                    "from": "least_connections",
                    "to": "predictive",
                    "start": 8,
                    "duration": 1
                }
            ]
        },
        {
            "name": "mixed_application_transition",
            "workload_transitions": [
                {
                    "from": lambda t: {
                        "web_traffic": 0.4 + 0.3 * np.sin(t * np.pi / 12),
                        "api_load": 0.5 + 0.2 * np.random.random()
                    },
                    "to": lambda t: {
                        "web_traffic": 0.6 + 0.2 * np.sin(t * np.pi / 12),
                        "api_load": 0.7 + 0.1 * np.random.random()
                    },
                    "start": 4,
                    "duration": 2
                },
                {
                    "from": lambda t: {
                        "database_load": 0.4 + 0.3 * np.sin(t * np.pi / 6),
                        "cache_hits": 0.7 if t % 3 == 0 else 0.3
                    },
                    "to": lambda t: {
                        "database_load": 0.6 + 0.2 * np.sin(t * np.pi / 6),
                        "cache_hits": 0.8 if t % 2 == 0 else 0.4
                    },
                    "start": 6,
                    "duration": 2
                }
            ],
            "resource_transitions": [
                {
                    "type": "network",
                    "from": lambda t: {"bandwidth": 1000, "latency": 10},
                    "to": lambda t: {"bandwidth": 2000, "latency": 5},
                    "start": 5,
                    "duration": 1
                },
                {
                    "type": "disk",
                    "from": lambda t: {"type": "ssd", "iops": 50000},
                    "to": lambda t: {"type": "nvme", "iops": 100000},
                    "start": 5,
                    "duration": 1
                }
            ],
            "strategy_transitions": [
                {
                    "from": "predictive",
                    "to": "response_time",
                    "start": 4,
                    "duration": 1
                },
                {
                    "from": "response_time",
                    "to": "weighted_round_robin",
                    "start": 6,
                    "duration": 1
                }
            ]
        }
    ]
    
    # Test each scenario
    scenario_results = {}
    for scenario in transition_scenarios:
        results = {
            "workload_metrics": [],
            "resource_metrics": [],
            "strategy_metrics": [],
            "performance_metrics": [],
            "transition_times": [],
            "timestamp": []
        }
        
        start_time = time.time()
        for t in range(24):  # Simulate 24 hours
            # Apply workload transitions
            workload_patterns = {}
            for transition in scenario["workload_transitions"]:
                if t < transition["start"]:
                    pattern = transition["from"](t)
                elif t >= transition["start"] + transition["duration"]:
                    pattern = transition["to"](t)
                else:
                    # During transition, blend patterns
                    progress = (t - transition["start"]) / transition["duration"]
                    from_pattern = transition["from"](t)
                    to_pattern = transition["to"](t)
                    pattern = {
                        k: from_pattern[k] * (1 - progress) + to_pattern[k] * progress
                        for k in set(from_pattern.keys()) | set(to_pattern.keys())
                    }
                workload_patterns.update(pattern)
            
            # Apply resource transitions
            resource_configs = {}
            for transition in scenario["resource_transitions"]:
                if t < transition["start"]:
                    config = transition["from"](t)
                elif t >= transition["start"] + transition["duration"]:
                    config = transition["to"](t)
                else:
                    # During transition, blend configurations
                    progress = (t - transition["start"]) / transition["duration"]
                    from_config = transition["from"](t)
                    to_config = transition["to"](t)
                    config = {
                        k: from_config[k] * (1 - progress) + to_config[k] * progress
                        for k in set(from_config.keys()) | set(to_config.keys())
                    }
                resource_configs[transition["type"]] = config
            
            # Apply strategy transitions
            current_strategy = None
            for transition in scenario["strategy_transitions"]:
                if t < transition["start"]:
                    current_strategy = transition["from"]
                elif t >= transition["start"] + transition["duration"]:
                    current_strategy = transition["to"]
                else:
                    # During transition, use intermediate strategy
                    current_strategy = "mixed"
            
            # Update node loads with all transitions
            for node in nodes:
                # Calculate total load considering all workload patterns
                total_load = max(
                    sum(workload_patterns.values()) / len(workload_patterns),
                    max(workload_patterns.values())
                )
                
                # Apply resource-specific configurations
                resource_load = NodeLoad(
                    cpu_usage=total_load * 0.8,
                    memory_usage=total_load * 0.7,
                    network_usage=total_load * 0.9,
                    active_connections=int(total_load * 1000),
                    resource_components={
                        **workload_patterns,
                        **{f"{k}_config": v for k, v in resource_configs.items()},
                        "current_strategy": current_strategy
                    }
                )
                
                benchmark_load_balancer.update_node_load(node.id, resource_load)
            
            # Collect metrics
            current_metrics = benchmark_load_balancer.get_detailed_metrics()
            results["workload_metrics"].append(workload_patterns)
            results["resource_metrics"].append(resource_configs)
            results["strategy_metrics"].append({"current_strategy": current_strategy})
            results["performance_metrics"].append(current_metrics)
            results["timestamp"].append(time.time() - start_time)
            
            # Track transition times
            if any(t == trans["start"] for trans in scenario["workload_transitions"] + 
                  scenario["resource_transitions"] + scenario["strategy_transitions"]):
                results["transition_times"].append(time.time() - start_time)
            
            await asyncio.sleep(0.1)
        
        scenario_results[scenario["name"]] = results
    
    # Analyze results and make assertions
    for scenario_name, results in scenario_results.items():
        # Check transition timing
        transition_times = results["transition_times"]
        if transition_times:
            avg_transition_time = np.mean(np.diff(transition_times))
            assert avg_transition_time < 1.0, f"{scenario_name}: Average transition time too high"
        
        # Check performance during transitions
        performance_metrics = results["performance_metrics"]
        success_rates = [m["strategy.success_rate"] for m in performance_metrics]
        assert np.mean(success_rates) > 0.8, f"{scenario_name}: Success rate too low"
        assert np.min(success_rates) > 0.7, f"{scenario_name}: Success rate dropped too low"
        
        # Check resource utilization
        resource_metrics = results["resource_metrics"]
        for resource_type in ["cpu", "memory", "network", "disk"]:
            if resource_type in resource_metrics[0]:
                utilizations = [m[resource_type]["utilization"] for m in resource_metrics]
                assert np.mean(utilizations) < 0.9, f"{scenario_name}: {resource_type} utilization too high"
    
    # Verify overall system stability
    metrics = benchmark_load_balancer.get_detailed_metrics()
    assert metrics["strategy.success_rate"] > 0.85, "Success rate too low after complex transitions"
    assert metrics["strategy.load_balance_score"] > 0.75, "Load balance too poor after complex transitions"
    assert metrics["strategy.resource_efficiency"] > 0.7, "Resource efficiency too low after complex transitions"