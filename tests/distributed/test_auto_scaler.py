import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from src.distributed.auto_scaler import AutoScaler, ScalingMetrics
from src.distributed.worker_registry import WorkerRegistry
from src.distributed.task_distributor import TaskDistributor
from src.cloud.manager import CloudManager

@pytest.fixture
def mock_worker_registry():
    """Create a mock worker registry."""
    registry = AsyncMock(spec=WorkerRegistry)
    registry.worker_count = 2
    registry.get_available_workers.return_value = [MagicMock(), MagicMock()]
    return registry

@pytest.fixture
def mock_task_distributor():
    """Create a mock task distributor."""
    distributor = MagicMock(spec=TaskDistributor)
    distributor.running_task_count = 0
    distributor.pending_task_count = 0
    return distributor

@pytest.fixture
def mock_cloud_manager():
    """Create a mock cloud manager."""
    manager = AsyncMock(spec=CloudManager)
    return manager

@pytest.fixture
def auto_scaler(mock_worker_registry, mock_task_distributor, mock_cloud_manager):
    """Create an auto-scaler instance with mocked dependencies."""
    return AutoScaler(
        worker_registry=mock_worker_registry,
        task_distributor=mock_task_distributor,
        cloud_manager=mock_cloud_manager,
        min_workers=1,
        max_workers=5,
        scale_up_threshold=0.8,
        scale_down_threshold=0.2,
        cooldown_period=60,
        metrics_window=60
    )

@pytest.mark.asyncio
async def test_start_stop_monitoring(auto_scaler):
    """Test starting and stopping the monitoring task."""
    await auto_scaler.start_monitoring()
    assert auto_scaler._monitoring_task is not None
    assert not auto_scaler._monitoring_task.done()
    
    await auto_scaler.stop_monitoring()
    assert auto_scaler._monitoring_task is None

@pytest.mark.asyncio
async def test_collect_metrics(auto_scaler, mock_worker_registry, mock_task_distributor):
    """Test metrics collection."""
    mock_worker_registry.worker_count = 3
    mock_worker_registry.get_available_workers.return_value = [MagicMock()]
    mock_task_distributor.running_task_count = 2
    mock_task_distributor.pending_task_count = 1
    
    await auto_scaler._collect_metrics()
    
    assert len(auto_scaler.metrics_history) == 1
    metrics = auto_scaler.metrics_history[0]
    assert metrics.current_workers == 3
    assert metrics.pending_tasks == 1
    assert metrics.running_tasks == 2
    assert metrics.worker_utilization == pytest.approx(0.666, abs=0.001)

@pytest.mark.asyncio
async def test_cleanup_old_metrics(auto_scaler):
    """Test cleanup of old metrics."""
    current_time = datetime.now()
    old_time = current_time - timedelta(seconds=120)
    
    # Add old and new metrics
    auto_scaler.metrics_history = [
        ScalingMetrics(
            current_workers=2,
            pending_tasks=0,
            running_tasks=0,
            avg_task_duration=0.0,
            worker_utilization=0.0,
            timestamp=old_time
        ),
        ScalingMetrics(
            current_workers=2,
            pending_tasks=0,
            running_tasks=0,
            avg_task_duration=0.0,
            worker_utilization=0.0,
            timestamp=current_time
        )
    ]
    
    auto_scaler._cleanup_old_metrics()
    assert len(auto_scaler.metrics_history) == 1
    assert auto_scaler.metrics_history[0].timestamp == current_time

@pytest.mark.asyncio
async def test_scale_up(auto_scaler, mock_cloud_manager):
    """Test scaling up when utilization is high."""
    auto_scaler.metrics_history = [
        ScalingMetrics(
            current_workers=2,
            pending_tasks=5,
            running_tasks=2,
            avg_task_duration=1.0,
            worker_utilization=0.9,  # Above threshold
            timestamp=datetime.now()
        )
    ]
    
    await auto_scaler._evaluate_scaling()
    mock_cloud_manager.scale_environment.assert_called_once()
    assert auto_scaler.last_scaling_time is not None

@pytest.mark.asyncio
async def test_scale_down(auto_scaler, mock_cloud_manager):
    """Test scaling down when utilization is low."""
    auto_scaler.metrics_history = [
        ScalingMetrics(
            current_workers=3,
            pending_tasks=0,
            running_tasks=0,
            avg_task_duration=1.0,
            worker_utilization=0.1,  # Below threshold
            timestamp=datetime.now()
        )
    ]
    
    await auto_scaler._evaluate_scaling()
    mock_cloud_manager.scale_environment.assert_called_once()
    assert auto_scaler.last_scaling_time is not None

@pytest.mark.asyncio
async def test_cooldown_period(auto_scaler, mock_cloud_manager):
    """Test that scaling doesn't occur during cooldown period."""
    auto_scaler.last_scaling_time = datetime.now() - timedelta(seconds=30)
    auto_scaler.cooldown_period = 60
    
    auto_scaler.metrics_history = [
        ScalingMetrics(
            current_workers=2,
            pending_tasks=5,
            running_tasks=2,
            avg_task_duration=1.0,
            worker_utilization=0.9,
            timestamp=datetime.now()
        )
    ]
    
    await auto_scaler._evaluate_scaling()
    mock_cloud_manager.scale_environment.assert_not_called()

@pytest.mark.asyncio
async def test_get_scaling_metrics(auto_scaler):
    """Test getting current scaling metrics."""
    current_time = datetime.now()
    auto_scaler.metrics_history = [
        ScalingMetrics(
            current_workers=2,
            pending_tasks=1,
            running_tasks=1,
            avg_task_duration=1.0,
            worker_utilization=0.5,
            timestamp=current_time
        )
    ]
    auto_scaler.last_scaling_time = current_time
    
    metrics = auto_scaler.get_scaling_metrics()
    assert metrics["current_workers"] == 2
    assert metrics["pending_tasks"] == 1
    assert metrics["running_tasks"] == 1
    assert metrics["worker_utilization"] == 0.5
    assert metrics["last_scaling_time"] == current_time.isoformat()

@pytest.mark.asyncio
async def test_min_max_worker_constraints(auto_scaler, mock_cloud_manager):
    """Test that scaling respects min and max worker constraints."""
    # Try to scale down below min_workers
    auto_scaler.metrics_history = [
        ScalingMetrics(
            current_workers=1,  # Already at min_workers
            pending_tasks=0,
            running_tasks=0,
            avg_task_duration=1.0,
            worker_utilization=0.1,  # Below threshold
            timestamp=datetime.now()
        )
    ]
    
    await auto_scaler._evaluate_scaling()
    mock_cloud_manager.scale_environment.assert_not_called()
    
    # Try to scale up above max_workers
    auto_scaler.metrics_history = [
        ScalingMetrics(
            current_workers=5,  # At max_workers
            pending_tasks=10,
            running_tasks=5,
            avg_task_duration=1.0,
            worker_utilization=0.9,  # Above threshold
            timestamp=datetime.now()
        )
    ]
    
    await auto_scaler._evaluate_scaling()
    mock_cloud_manager.scale_environment.assert_not_called()

@pytest.mark.asyncio
async def test_concurrent_scaling_operations(auto_scaler, mock_cloud_manager):
    """Test that concurrent scaling operations are prevented."""
    auto_scaler.metrics_history = [
        ScalingMetrics(
            current_workers=2,
            pending_tasks=5,
            running_tasks=2,
            avg_task_duration=1.0,
            worker_utilization=0.9,
            timestamp=datetime.now()
        )
    ]
    
    # Simulate concurrent scaling attempts
    tasks = [
        auto_scaler._evaluate_scaling(),
        auto_scaler._evaluate_scaling()
    ]
    await asyncio.gather(*tasks)
    
    # Only one scaling operation should have occurred
    assert mock_cloud_manager.scale_environment.call_count == 1

@pytest.mark.asyncio
async def test_metrics_history_limits(auto_scaler):
    """Test that metrics history is properly limited."""
    current_time = datetime.now()
    
    # Add more metrics than the window can hold
    for i in range(10):
        auto_scaler.metrics_history.append(
            ScalingMetrics(
                current_workers=2,
                pending_tasks=0,
                running_tasks=0,
                avg_task_duration=1.0,
                worker_utilization=0.5,
                timestamp=current_time - timedelta(seconds=i * 10)
            )
        )
    
    auto_scaler._cleanup_old_metrics()
    assert len(auto_scaler.metrics_history) <= auto_scaler.metrics_window / 10

@pytest.mark.asyncio
async def test_error_handling(auto_scaler, mock_cloud_manager):
    """Test error handling during scaling operations."""
    # Simulate cloud manager failure
    mock_cloud_manager.scale_environment.side_effect = Exception("Cloud error")
    
    auto_scaler.metrics_history = [
        ScalingMetrics(
            current_workers=2,
            pending_tasks=5,
            running_tasks=2,
            avg_task_duration=1.0,
            worker_utilization=0.9,
            timestamp=datetime.now()
        )
    ]
    
    # Should not raise exception
    await auto_scaler._evaluate_scaling()
    
    # Should still be able to collect metrics after error
    await auto_scaler._collect_metrics()
    assert len(auto_scaler.metrics_history) > 0

@pytest.mark.asyncio
async def test_task_duration_impact(auto_scaler, mock_cloud_manager):
    """Test that task duration impacts scaling decisions."""
    # Long-running tasks should trigger scaling up
    auto_scaler.metrics_history = [
        ScalingMetrics(
            current_workers=2,
            pending_tasks=2,
            running_tasks=2,
            avg_task_duration=300.0,  # 5 minutes average
            worker_utilization=0.7,  # Below threshold but with long tasks
            timestamp=datetime.now()
        )
    ]
    
    await auto_scaler._evaluate_scaling()
    mock_cloud_manager.scale_environment.assert_called_once()

@pytest.mark.asyncio
async def test_rapid_workload_changes(auto_scaler, mock_cloud_manager):
    """Test handling of rapid workload changes."""
    # Simulate rapid workload increase
    for i in range(3):
        auto_scaler.metrics_history.append(
            ScalingMetrics(
                current_workers=2,
                pending_tasks=i * 5,
                running_tasks=2,
                avg_task_duration=1.0,
                worker_utilization=0.5 + (i * 0.2),
                timestamp=datetime.now() - timedelta(seconds=i * 10)
            )
        )
    
    await auto_scaler._evaluate_scaling()
    # Should not scale immediately due to cooldown
    mock_cloud_manager.scale_environment.assert_not_called()

@pytest.mark.asyncio
async def test_empty_metrics_history(auto_scaler, mock_cloud_manager):
    """Test behavior with empty metrics history."""
    auto_scaler.metrics_history = []
    await auto_scaler._evaluate_scaling()
    mock_cloud_manager.scale_environment.assert_not_called()
    
    # Should still be able to collect new metrics
    await auto_scaler._collect_metrics()
    assert len(auto_scaler.metrics_history) == 1 