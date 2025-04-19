import pytest
import asyncio
from datetime import datetime, timedelta
from src.distributed.worker_registry import WorkerRegistry, WorkerNode
from src.distributed.task_distributor import TaskDistributor, TestTask
from src.distributed.result_aggregator import ResultAggregator, TestResult

@pytest.fixture
async def worker_registry():
    """Create a worker registry for testing."""
    registry = WorkerRegistry()
    await registry.start_cleanup_task()
    yield registry
    await registry.stop_cleanup_task()

@pytest.fixture
async def task_distributor(worker_registry):
    """Create a task distributor for testing."""
    return TaskDistributor(worker_registry)

@pytest.fixture
def result_aggregator():
    """Create a result aggregator for testing."""
    return ResultAggregator()

@pytest.fixture
def sample_workers():
    """Create sample worker nodes for testing."""
    return [
        WorkerNode(
            id=f"worker{i}",
            host="localhost",
            port=8000 + i,
            capabilities={
                "os": "linux",
                "browser": "chrome",
                "memory": "8GB"
            }
        ) for i in range(3)
    ]

@pytest.fixture
def sample_tasks():
    """Create sample test tasks for testing."""
    return [
        TestTask(
            id=f"task{i}",
            type="api",
            priority=i + 1,
            dependencies=[] if i == 0 else [f"task{i-1}"]
        ) for i in range(5)
    ]

@pytest.mark.asyncio
async def test_worker_registration(worker_registry, sample_workers):
    """Test worker registration functionality."""
    # Register workers
    for worker in sample_workers:
        await worker_registry.register_worker(worker)
    
    # Verify registration
    assert worker_registry.worker_count == len(sample_workers)
    
    # Get available workers
    available = await worker_registry.get_available_workers()
    assert len(available) == len(sample_workers)
    
    # Update worker status
    await worker_registry.update_worker_status(sample_workers[0].id, "busy")
    available = await worker_registry.get_available_workers()
    assert len(available) == len(sample_workers) - 1

@pytest.mark.asyncio
async def test_task_distribution(task_distributor, sample_tasks):
    """Test task distribution functionality."""
    # Add tasks
    for task in sample_tasks:
        await task_distributor.add_task(task)
    
    # Verify task queue
    assert task_distributor.pending_task_count == len(sample_tasks)
    
    # Distribute tasks
    await task_distributor.distribute_tasks()
    
    # Verify task distribution
    assert task_distributor.running_task_count > 0

@pytest.mark.asyncio
async def test_result_aggregation(result_aggregator):
    """Test result aggregation functionality."""
    # Create sample results
    results = [
        TestResult(
            test_id="test1",
            node_id="worker1",
            status="passed",
            duration=1.0,
            timestamp=datetime.now(),
            metrics={"response_time": 0.5}
        ),
        TestResult(
            test_id="test1",
            node_id="worker2",
            status="failed",
            duration=2.0,
            timestamp=datetime.now(),
            error="Test failed",
            metrics={"response_time": 1.0}
        )
    ]
    
    # Add results
    for result in results:
        await result_aggregator.add_result(result)
    
    # Get test summary
    summary = result_aggregator.get_test_summary("test1")
    assert summary["total_runs"] == 2
    assert summary["pass_count"] == 1
    assert summary["fail_count"] == 1
    
    # Get overall summary
    overall = result_aggregator.get_overall_summary()
    assert overall["total_tests"] == 1
    assert overall["total_runs"] == 2

@pytest.mark.asyncio
async def test_integration(worker_registry, task_distributor, result_aggregator, sample_workers, sample_tasks):
    """Test integration of all components."""
    # Register workers
    for worker in sample_workers:
        await worker_registry.register_worker(worker)
    
    # Add tasks
    for task in sample_tasks:
        await task_distributor.add_task(task)
    
    # Distribute tasks
    await task_distributor.distribute_tasks()
    
    # Simulate task completion
    for task in sample_tasks:
        result = TestResult(
            test_id=task.id,
            node_id=task.assigned_worker,
            status="passed",
            duration=1.0,
            timestamp=datetime.now()
        )
        await result_aggregator.add_result(result)
        await task_distributor.complete_task(task.id, {"status": "passed"})
    
    # Verify results
    summary = result_aggregator.get_overall_summary()
    assert summary["total_tests"] == len(sample_tasks)
    assert summary["pass_count"] == len(sample_tasks)

@pytest.mark.asyncio
async def test_error_handling(task_distributor, sample_tasks):
    """Test error handling in task distribution."""
    # Add task
    task = sample_tasks[0]
    await task_distributor.add_task(task)
    
    # Simulate task failure
    await task_distributor.fail_task(task.id, "Test failed")
    
    # Verify retry
    assert task_distributor.pending_task_count == 1
    assert task.retry_count == 1

@pytest.mark.asyncio
async def test_worker_cleanup(worker_registry, sample_workers):
    """Test worker cleanup functionality."""
    # Register workers
    for worker in sample_workers:
        await worker_registry.register_worker(worker)
    
    # Simulate worker inactivity
    sample_workers[0].last_heartbeat = datetime.now() - timedelta(minutes=5)
    
    # Wait for cleanup
    await asyncio.sleep(35)  # Slightly more than heartbeat interval
    
    # Verify cleanup
    assert worker_registry.worker_count == len(sample_workers) - 1 