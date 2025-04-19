# Distributed Testing API Documentation

## Overview

PulseQ's distributed testing framework enables parallel test execution across multiple nodes, providing scalability and efficiency for large test suites. This document covers the core components and their APIs.

## Core Components

### 1. DistributedTestRunner

The main orchestrator for distributed test execution.

```python
from pulseq.distributed.test_runner import DistributedTestRunner, TestNode

# Initialize runner
runner = DistributedTestRunner()

# Add test nodes
node = TestNode(
    id="node1",
    host="localhost",
    port=8000,
    capabilities={"os": "linux", "browser": "chrome"}
)
await runner.add_node(node)

# Run tests
results = await runner.run_tests()
```

#### Key Methods

- `add_node(node: TestNode)`: Register a new test node
- `remove_node(node_id: str)`: Remove a node from the cluster
- `run_test(test: dict)`: Execute a single test
- `run_tests()`: Execute all scheduled tests
- `run_test_with_retry(test: dict)`: Execute a test with retry mechanism

### 2. NodeManager

Manages node health and communication.

```python
from pulseq.distributed.node_manager import NodeManager

# Initialize manager
manager = NodeManager()

# Register node
await manager.register_node(node)

# Start monitoring
await manager.start_monitoring()

# Get node status
status = manager.get_node_status("node1")
```

#### Key Methods

- `register_node(node: TestNode)`: Register a new node
- `start_monitoring()`: Begin node health monitoring
- `process_heartbeat(node_id: str)`: Process node heartbeat
- `get_node_status(node_id: str)`: Get current node status
- `get_available_nodes()`: Get all active nodes

### 3. TestScheduler

Manages test distribution and scheduling.

```python
from pulseq.distributed.test_scheduler import TestScheduler

# Initialize scheduler
scheduler = TestScheduler()

# Schedule test
test = {
    "id": "test1",
    "name": "api_test",
    "duration": 1.0,
    "priority": "high",
    "requirements": {"os": "linux"}
}
await scheduler.schedule_test(test)

# Get node load
load = scheduler.get_node_load("node1")
```

#### Key Methods

- `schedule_test(test: dict)`: Schedule a test for execution
- `get_node_tests(node_id: str)`: Get tests assigned to a node
- `get_node_load(node_id: str)`: Get current node load
- `get_node_loads()`: Get load distribution across all nodes

### 4. ResultsAggregator

Collects and analyzes test results.

```python
from pulseq.distributed.results_aggregator import ResultsAggregator, TestResult

# Initialize aggregator
aggregator = ResultsAggregator()

# Add result
result = TestResult(
    test_id="test1",
    node_id="node1",
    status="passed",
    duration=1.0,
    timestamp=datetime.now(),
    metrics={"response_time": 0.5}
)
aggregator.add_result(result)

# Get summary
summary = aggregator.get_summary()
```

#### Key Methods

- `add_result(result: TestResult)`: Add a test result
- `get_results()`: Get all test results
- `get_summary()`: Get overall test summary
- `get_node_summary(node_id: str)`: Get node-specific summary
- `get_metrics_summary()`: Get metrics analysis

## Configuration Options

### Node Configuration

```python
node_config = {
    "id": "node1",
    "host": "localhost",
    "port": 8000,
    "capabilities": {
        "os": "linux",
        "browser": "chrome",
        "memory": "8GB"
    },
    "max_concurrent_tests": 5
}
```

### Test Configuration

```python
test_config = {
    "id": "test1",
    "name": "api_test",
    "duration": 1.0,
    "priority": "high",
    "requirements": {
        "os": "linux",
        "browser": "chrome"
    },
    "timeout": 30,
    "max_retries": 3,
    "metrics": ["response_time", "memory_usage"]
}
```

### Framework Configuration

```python
framework_config = {
    "heartbeat_interval": 30,  # seconds
    "node_timeout": 60,        # seconds
    "load_balancing_strategy": "round_robin",
    "result_aggregation": {
        "enabled": True,
        "interval": 5,         # seconds
        "persist_results": True
    }
}
```

## Usage Examples

### Basic Test Execution

```python
from pulseq.distributed import DistributedTestRunner, TestNode

async def run_basic_test():
    # Initialize components
    runner = DistributedTestRunner()

    # Add nodes
    node = TestNode("node1", "localhost", 8000)
    await runner.add_node(node)

    # Define test
    test = {
        "id": "test1",
        "name": "basic_test",
        "duration": 1.0
    }

    # Run test
    result = await runner.run_test(test)
    print(f"Test status: {result.status}")
```

### Distributed Load Testing

```python
from pulseq.distributed import DistributedTestRunner, TestScheduler

async def run_load_test():
    # Initialize components
    runner = DistributedTestRunner()
    scheduler = TestScheduler()

    # Add multiple nodes
    for i in range(3):
        node = TestNode(f"node{i}", "localhost", 8000 + i)
        await runner.add_node(node)

    # Schedule multiple tests
    for i in range(100):
        test = {
            "id": f"load_test_{i}",
            "name": "api_load_test",
            "duration": 0.5,
            "priority": "high"
        }
        await scheduler.schedule_test(test)

    # Run tests
    results = await runner.run_tests()

    # Analyze results
    print(f"Total tests: {len(results)}")
    print(f"Pass rate: {results.get_summary()['pass_rate']}%")
```

### Custom Metrics Collection

```python
from pulseq.distributed import ResultsAggregator, TestResult

async def collect_metrics():
    aggregator = ResultsAggregator()

    # Add results with custom metrics
    result = TestResult(
        test_id="test1",
        node_id="node1",
        status="passed",
        duration=1.0,
        timestamp=datetime.now(),
        metrics={
            "response_time": 0.5,
            "memory_usage": 100,
            "cpu_usage": 30,
            "network_latency": 50
        }
    )
    aggregator.add_result(result)

    # Get metrics analysis
    metrics = aggregator.get_metrics_summary()
    print(f"Average response time: {metrics['response_time']['avg']}ms")
    print(f"Max memory usage: {metrics['memory_usage']['max']}MB")
```

## Best Practices

1. **Node Management**

   - Register nodes with appropriate capabilities
   - Monitor node health regularly
   - Implement proper error handling for node failures

2. **Test Distribution**

   - Use priority levels for critical tests
   - Consider node capabilities when scheduling tests
   - Monitor load distribution across nodes

3. **Result Analysis**

   - Collect relevant metrics for analysis
   - Use summaries for quick status checks
   - Implement proper result persistence

4. **Error Handling**
   - Implement retry mechanisms for transient failures
   - Set appropriate timeouts
   - Log detailed error information

## Troubleshooting

### Common Issues

1. **Node Connection Issues**

   - Verify network connectivity
   - Check node configuration
   - Monitor node health status

2. **Test Distribution Problems**

   - Check node capabilities
   - Verify load balancing settings
   - Monitor node load distribution

3. **Result Aggregation Issues**
   - Verify result format
   - Check aggregation interval
   - Monitor memory usage

### Debugging Tips

1. Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Monitor node status:

```python
status = manager.get_node_status("node1")
print(f"Node status: {status}")
```

3. Check test distribution:

```python
loads = scheduler.get_node_loads()
print(f"Node loads: {loads}")
```
