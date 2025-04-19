# Auto-Scaler Documentation

## Overview

The Auto-Scaler is a dynamic scaling component that automatically adjusts the number of worker nodes in the distributed testing system based on workload metrics. It monitors system utilization and scales resources up or down to maintain optimal performance while minimizing costs.

## Key Features

- Dynamic worker scaling based on workload metrics
- Configurable scaling thresholds and limits
- Cooldown period to prevent rapid scaling fluctuations
- Metrics history tracking for informed scaling decisions
- Asynchronous monitoring and scaling operations

## Configuration Parameters

### AutoScaler Initialization

```python
auto_scaler = AutoScaler(
    worker_registry=worker_registry,
    task_distributor=task_distributor,
    cloud_manager=cloud_manager,
    min_workers=1,              # Minimum number of workers
    max_workers=10,             # Maximum number of workers
    scale_up_threshold=0.8,     # Utilization threshold for scaling up
    scale_down_threshold=0.2,   # Utilization threshold for scaling down
    cooldown_period=300,        # Seconds between scaling operations
    metrics_window=300          # Window for metrics collection (seconds)
)
```

### Parameter Descriptions

- `min_workers`: Minimum number of worker nodes to maintain
- `max_workers`: Maximum number of worker nodes allowed
- `scale_up_threshold`: Worker utilization threshold (0.0-1.0) that triggers scaling up
- `scale_down_threshold`: Worker utilization threshold (0.0-1.0) that triggers scaling down
- `cooldown_period`: Minimum time (seconds) between scaling operations
- `metrics_window`: Time window (seconds) for collecting and analyzing metrics

## Usage Guide

### Starting the Auto-Scaler

```python
await auto_scaler.start_monitoring()
```

### Stopping the Auto-Scaler

```python
await auto_scaler.stop_monitoring()
```

### Getting Current Metrics

```python
metrics = auto_scaler.get_scaling_metrics()
```

## Metrics and Scaling Logic

### Collected Metrics

- Current number of workers
- Number of pending tasks
- Number of running tasks
- Average task duration
- Worker utilization percentage
- Timestamp of last scaling operation

### Scaling Decisions

The auto-scaler makes scaling decisions based on the following rules:

1. **Scale Up Conditions**:

   - Worker utilization exceeds `scale_up_threshold`
   - Number of pending tasks is greater than 0
   - Current workers are below `max_workers`
   - Cooldown period has elapsed

2. **Scale Down Conditions**:
   - Worker utilization is below `scale_down_threshold`
   - Current workers are above `min_workers`
   - Cooldown period has elapsed

## Best Practices

### Configuration Recommendations

1. Set `min_workers` based on minimum required capacity
2. Set `max_workers` based on budget constraints
3. Adjust thresholds based on workload patterns:
   - Higher `scale_up_threshold` for cost optimization
   - Lower `scale_down_threshold` for performance optimization
4. Set `cooldown_period` to prevent rapid scaling fluctuations
5. Adjust `metrics_window` based on workload variability

### Monitoring and Maintenance

1. Regularly review scaling metrics
2. Adjust thresholds based on observed patterns
3. Monitor cloud costs and adjust `max_workers` accordingly
4. Review scaling logs for unusual patterns

## Error Handling

The auto-scaler includes comprehensive error handling:

- Failed scaling operations are logged
- Monitoring continues despite temporary failures
- Metrics collection errors are handled gracefully
- Scaling operations are protected by locks

## Integration

The auto-scaler integrates with:

- Worker Registry for worker management
- Task Distributor for workload metrics
- Cloud Manager for resource scaling

## Example Usage

```python
from src.distributed.auto_scaler import AutoScaler
from src.distributed.worker_registry import WorkerRegistry
from src.distributed.task_distributor import TaskDistributor
from src.cloud.manager import CloudManager

# Initialize components
worker_registry = WorkerRegistry()
task_distributor = TaskDistributor()
cloud_manager = CloudManager()

# Create auto-scaler
auto_scaler = AutoScaler(
    worker_registry=worker_registry,
    task_distributor=task_distributor,
    cloud_manager=cloud_manager,
    min_workers=2,
    max_workers=10,
    scale_up_threshold=0.8,
    scale_down_threshold=0.2,
    cooldown_period=300,
    metrics_window=300
)

# Start monitoring
await auto_scaler.start_monitoring()

# Get current metrics
metrics = auto_scaler.get_scaling_metrics()
print(f"Current workers: {metrics['current_workers']}")
print(f"Worker utilization: {metrics['worker_utilization']}")

# Stop monitoring when done
await auto_scaler.stop_monitoring()
```

## Troubleshooting

### Common Issues and Solutions

1. **Rapid Scaling Fluctuations**

   - Increase the `cooldown_period`
   - Adjust scaling thresholds
   - Review workload patterns

2. **High Cloud Costs**

   - Lower `max_workers`
   - Increase `scale_up_threshold`
   - Review workload distribution

3. **Performance Issues**

   - Lower `scale_down_threshold`
   - Increase `min_workers`
   - Review task distribution

4. **Scaling Not Triggering**
   - Check metrics collection
   - Verify threshold values
   - Review cooldown period

## Support

For additional support or questions about the auto-scaler implementation, please refer to:

- Project documentation
- Issue tracker
- Team communication channels
