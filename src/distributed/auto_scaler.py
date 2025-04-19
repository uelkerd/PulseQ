import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from ..cloud.manager import CloudManager
from .task_distributor import TaskDistributor
from .worker_registry import WorkerRegistry

logger = logging.getLogger(__name__)


@dataclass
class ScalingMetrics:
    """Metrics used for auto-scaling decisions."""

    current_workers: int
    pending_tasks: int
    running_tasks: int
    avg_task_duration: float
    worker_utilization: float
    timestamp: datetime


class AutoScaler:
    """Manages dynamic scaling of worker nodes based on workload."""

    def __init__(
        self,
        worker_registry: WorkerRegistry,
        task_distributor: TaskDistributor,
        cloud_manager: CloudManager,
        min_workers: int = 1,
        max_workers: int = 10,
        scale_up_threshold: float = 0.8,
        scale_down_threshold: float = 0.2,
        cooldown_period: int = 300,  # 5 minutes
        metrics_window: int = 300,  # 5 minutes
    ):
        self.worker_registry = worker_registry
        self.task_distributor = task_distributor
        self.cloud_manager = cloud_manager
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.cooldown_period = cooldown_period
        self.metrics_window = metrics_window

        self.metrics_history: list[ScalingMetrics] = []
        self.last_scaling_time: Optional[datetime] = None
        self._scaling_lock = asyncio.Lock()
        self._monitoring_task: Optional[asyncio.Task] = None

    async def start_monitoring(self) -> None:
        """Start the auto-scaling monitoring task."""
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitor_workload())

    async def stop_monitoring(self) -> None:
        """Stop the auto-scaling monitoring task."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None

    async def _monitor_workload(self) -> None:
        """Monitor workload and trigger scaling when needed."""
        while True:
            try:
                await self._collect_metrics()
                await self._evaluate_scaling()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring task: {str(e)}")
                await asyncio.sleep(60)

    async def _collect_metrics(self) -> None:
        """Collect current workload metrics."""
        current_time = datetime.now()

        # Calculate worker utilization
        active_workers = await self.worker_registry.get_available_workers()
        total_workers = self.worker_registry.worker_count
        worker_utilization = (
            (total_workers - len(active_workers)) / total_workers
            if total_workers > 0
            else 0
        )

        # Calculate average task duration
        running_tasks = self.task_distributor.running_task_count
        pending_tasks = self.task_distributor.pending_task_count

        metrics = ScalingMetrics(
            current_workers=total_workers,
            pending_tasks=pending_tasks,
            running_tasks=running_tasks,
            avg_task_duration=self._calculate_avg_task_duration(),
            worker_utilization=worker_utilization,
            timestamp=current_time,
        )

        self.metrics_history.append(metrics)
        self._cleanup_old_metrics()

    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than the metrics window."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=self.metrics_window)
        self.metrics_history = [
            m for m in self.metrics_history if m.timestamp >= cutoff_time
        ]

    def _calculate_avg_task_duration(self) -> float:
        """Calculate average task duration from recent metrics."""
        if not self.metrics_history:
            return 0.0

        recent_metrics = self.metrics_history[-5:]  # Last 5 minutes
        total_duration = sum(m.avg_task_duration for m in recent_metrics)
        return total_duration / len(recent_metrics)

    async def _evaluate_scaling(self) -> None:
        """Evaluate if scaling is needed based on current metrics."""
        if not self.metrics_history:
            return

        current_metrics = self.metrics_history[-1]

        # Check if we're in cooldown period
        if self.last_scaling_time:
            time_since_last_scale = (
                datetime.now() - self.last_scaling_time
            ).total_seconds()
            if time_since_last_scale < self.cooldown_period:
                return

        async with self._scaling_lock:
            # Scale up if utilization is high and we have pending tasks
            if (
                current_metrics.worker_utilization > self.scale_up_threshold
                and current_metrics.pending_tasks > 0
                and current_metrics.current_workers < self.max_workers
            ):
                await self._scale_up()

            # Scale down if utilization is low
            elif (
                current_metrics.worker_utilization < self.scale_down_threshold
                and current_metrics.current_workers > self.min_workers
            ):
                await self._scale_down()

    async def _scale_up(self) -> None:
        """Scale up the number of worker nodes."""
        try:
            current_workers = self.worker_registry.worker_count
            new_workers = min(
                self.max_workers - current_workers,
                max(1, int(current_workers * 0.5)),  # Scale up by 50% or 1
            )

            if new_workers > 0:
                logger.info(f"Scaling up by {new_workers} workers")
                await self.cloud_manager.scale_environment(
                    "test-environment", current_workers + new_workers
                )
                self.last_scaling_time = datetime.now()

        except Exception as e:
            logger.error(f"Error scaling up: {str(e)}")

    async def _scale_down(self) -> None:
        """Scale down the number of worker nodes."""
        try:
            current_workers = self.worker_registry.worker_count
            workers_to_remove = min(
                current_workers - self.min_workers,
                max(1, int(current_workers * 0.25)),  # Scale down by 25% or 1
            )

            if workers_to_remove > 0:
                logger.info(f"Scaling down by {workers_to_remove} workers")
                await self.cloud_manager.scale_environment(
                    "test-environment", current_workers - workers_to_remove
                )
                self.last_scaling_time = datetime.now()

        except Exception as e:
            logger.error(f"Error scaling down: {str(e)}")

    def get_scaling_metrics(self) -> Dict[str, Any]:
        """Get current scaling metrics for monitoring."""
        if not self.metrics_history:
            return {}

        current_metrics = self.metrics_history[-1]
        return {
            "current_workers": current_metrics.current_workers,
            "pending_tasks": current_metrics.pending_tasks,
            "running_tasks": current_metrics.running_tasks,
            "worker_utilization": current_metrics.worker_utilization,
            "avg_task_duration": current_metrics.avg_task_duration,
            "last_scaling_time": (
                self.last_scaling_time.isoformat() if self.last_scaling_time else None
            ),
            "metrics_window": self.metrics_window,
            "cooldown_period": self.cooldown_period,
        }
