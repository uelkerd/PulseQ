import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .worker_registry import WorkerNode, WorkerRegistry

logger = logging.getLogger(__name__)


@dataclass
class TestTask:
    """Represents a test task in the distributed testing system."""

    id: str
    type: str
    priority: int = 1
    dependencies: List[str] = None
    timeout: int = 300  # seconds
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    assigned_worker: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

    def is_ready(self, completed_tasks: List[str]) -> bool:
        """Check if the task is ready to be executed."""
        return all(dep in completed_tasks for dep in self.dependencies)

    def can_retry(self) -> bool:
        """Check if the task can be retried."""
        return self.retry_count < self.max_retries


class TaskDistributor:
    """Manages test task distribution across worker nodes."""

    def __init__(self, worker_registry: WorkerRegistry):
        self.worker_registry = worker_registry
        self.tasks: Dict[str, TestTask] = {}
        self.task_queue = asyncio.PriorityQueue()
        self.completed_tasks: List[str] = []
        self._distribution_lock = asyncio.Lock()

    async def add_task(self, task: TestTask) -> None:
        """Add a new task to the distribution system."""
        self.tasks[task.id] = task
        await self.task_queue.put((task.priority, task.id))
        logger.info(f"Added task {task.id} with priority {task.priority}")

    async def distribute_tasks(self) -> None:
        """Distribute tasks to available workers."""
        async with self._distribution_lock:
            while not self.task_queue.empty():
                _, task_id = await self.task_queue.get()
                task = self.tasks[task_id]

                if not task.is_ready(self.completed_tasks):
                    # Task has unmet dependencies, put it back in queue
                    await self.task_queue.put((task.priority, task.id))
                    continue

                available_workers = await self.worker_registry.get_available_workers()
                if not available_workers:
                    # No workers available, put task back in queue
                    await self.task_queue.put((task.priority, task.id))
                    break

                # Find best worker for the task
                worker = self._find_best_worker(task, available_workers)
                if worker:
                    await self._assign_task_to_worker(task, worker)
                else:
                    # No suitable worker found, put task back in queue
                    await self.task_queue.put((task.priority, task.id))

    def _find_best_worker(
        self, task: TestTask, workers: List[WorkerNode]
    ) -> Optional[WorkerNode]:
        """Find the best worker for a given task."""
        if not workers:
            return None

        # Simple round-robin selection for now
        # TODO: Implement more sophisticated worker selection based on:
        # - Worker capabilities
        # - Current load
        # - Task requirements
        # - Network latency
        return workers[0]

    async def _assign_task_to_worker(self, task: TestTask, worker: WorkerNode) -> None:
        """Assign a task to a worker."""
        task.assigned_worker = worker.id
        task.status = "assigned"
        task.start_time = datetime.now()
        worker.tasks.append(task.id)
        worker.current_load += 0.1  # Simple load calculation
        await self.worker_registry.update_worker_status(worker.id, "busy")
        logger.info(f"Assigned task {task.id} to worker {worker.id}")

    async def complete_task(self, task_id: str, result: Dict[str, Any]) -> None:
        """Mark a task as completed."""
        if task_id not in self.tasks:
            logger.warning(f"Attempted to complete unknown task {task_id}")
            return

        task = self.tasks[task_id]
        task.status = "completed"
        task.end_time = datetime.now()
        task.result = result

        if task.assigned_worker:
            worker = await self.worker_registry.get_worker(task.assigned_worker)
            if worker:
                worker.tasks.remove(task_id)
                worker.current_load -= 0.1
                await self.worker_registry.update_worker_status(worker.id, "idle")

        self.completed_tasks.append(task_id)
        logger.info(f"Completed task {task_id}")

    async def fail_task(self, task_id: str, error: str) -> None:
        """Mark a task as failed."""
        if task_id not in self.tasks:
            logger.warning(f"Attempted to fail unknown task {task_id}")
            return

        task = self.tasks[task_id]
        task.status = "failed"
        task.result = {"error": error}

        if task.can_retry():
            task.retry_count += 1
            task.status = "pending"
            task.assigned_worker = None
            await self.task_queue.put((task.priority, task.id))
            logger.info(f"Retrying task {task_id} (attempt {task.retry_count})")
        else:
            logger.error(f"Task {task_id} failed permanently: {error}")

    @property
    def pending_task_count(self) -> int:
        """Get the number of pending tasks."""
        return len([t for t in self.tasks.values() if t.status == "pending"])

    @property
    def running_task_count(self) -> int:
        """Get the number of running tasks."""
        return len([t for t in self.tasks.values() if t.status == "assigned"])

    @property
    def completed_task_count(self) -> int:
        """Get the number of completed tasks."""
        return len(self.completed_tasks)
