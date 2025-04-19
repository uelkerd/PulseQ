from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class WorkerNode:
    """Represents a worker node in the distributed testing system."""
    id: str
    host: str
    port: int
    capabilities: Dict[str, Any]
    status: str = "idle"
    last_heartbeat: Optional[datetime] = None
    current_load: float = 0.0
    max_load: float = 1.0
    tasks: list = None

    def __post_init__(self):
        if self.tasks is None:
            self.tasks = []

    def update_heartbeat(self):
        """Update the last heartbeat timestamp."""
        self.last_heartbeat = datetime.now()

    def is_available(self) -> bool:
        """Check if the node is available for new tasks."""
        return (
            self.status == "idle" and
            self.current_load < self.max_load and
            (self.last_heartbeat is None or
             datetime.now() - self.last_heartbeat < timedelta(seconds=30))
        )

class WorkerRegistry:
    """Manages worker nodes in the distributed testing system."""

    def __init__(self):
        self._workers: Dict[str, WorkerNode] = {}
        self._heartbeat_interval = 30  # seconds
        self._cleanup_task = None

    async def register_worker(self, worker: WorkerNode) -> None:
        """Register a new worker node."""
        worker.update_heartbeat()
        self._workers[worker.id] = worker
        logger.info(f"Registered worker {worker.id} at {worker.host}:{worker.port}")

    async def unregister_worker(self, worker_id: str) -> None:
        """Unregister a worker node."""
        if worker_id in self._workers:
            del self._workers[worker_id]
            logger.info(f"Unregistered worker {worker_id}")

    async def update_worker_status(self, worker_id: str, status: str) -> None:
        """Update the status of a worker node."""
        if worker_id in self._workers:
            self._workers[worker_id].status = status
            self._workers[worker_id].update_heartbeat()
            logger.debug(f"Updated worker {worker_id} status to {status}")

    async def get_available_workers(self) -> list:
        """Get list of available worker nodes."""
        return [
            worker for worker in self._workers.values()
            if worker.is_available()
        ]

    async def get_worker(self, worker_id: str) -> Optional[WorkerNode]:
        """Get a worker node by ID."""
        return self._workers.get(worker_id)

    async def start_cleanup_task(self) -> None:
        """Start the cleanup task for inactive workers."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_inactive_workers())

    async def stop_cleanup_task(self) -> None:
        """Stop the cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None

    async def _cleanup_inactive_workers(self) -> None:
        """Clean up inactive workers."""
        while True:
            try:
                current_time = datetime.now()
                inactive_workers = [
                    worker_id for worker_id, worker in self._workers.items()
                    if worker.last_heartbeat and
                    current_time - worker.last_heartbeat > timedelta(seconds=self._heartbeat_interval * 2)
                ]
                
                for worker_id in inactive_workers:
                    await self.unregister_worker(worker_id)
                    logger.warning(f"Removed inactive worker {worker_id}")
                
                await asyncio.sleep(self._heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {str(e)}")
                await asyncio.sleep(self._heartbeat_interval)

    @property
    def worker_count(self) -> int:
        """Get the total number of registered workers."""
        return len(self._workers)

    @property
    def active_worker_count(self) -> int:
        """Get the number of active workers."""
        return len([w for w in self._workers.values() if w.status != "offline"]) 