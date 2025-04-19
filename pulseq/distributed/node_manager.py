"""
Node manager implementation for distributed testing.

This module handles node communication, health checks, and node management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .test_runner import TestNode


class NodeManager:
    """Manages test nodes and their communication."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the node manager.

        Args:
            config: Configuration dictionary containing node settings
        """
        self.config = config
        self.nodes: Dict[str, TestNode] = {}
        self.logger = logging.getLogger(__name__)
        self.heartbeat_interval = config.get("heartbeat_interval", 30)
        self.node_timeout = config.get("node_timeout", 60)

    async def start(self) -> None:
        """Start the node manager and begin monitoring nodes."""
        self.logger.info("Starting node manager")
        asyncio.create_task(self._monitor_nodes())

    async def register_node(self, node: TestNode) -> None:
        """
        Register a new node with the manager.

        Args:
            node: TestNode instance to register
        """
        self.nodes[node.id] = node
        node.last_heartbeat = datetime.now()
        self.logger.info(f"Registered node {node.id} at {node.host}:{node.port}")

    async def update_node_status(self, node_id: str, status: str) -> None:
        """
        Update a node's status.

        Args:
            node_id: ID of the node to update
            status: New status for the node
        """
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            self.logger.debug(f"Updated node {node_id} status to {status}")

    async def receive_heartbeat(self, node_id: str) -> None:
        """
        Process a heartbeat from a node.

        Args:
            node_id: ID of the node sending the heartbeat
        """
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = datetime.now()
            self.logger.debug(f"Received heartbeat from node {node_id}")

    async def _monitor_nodes(self) -> None:
        """Monitor node health and handle timeouts."""
        while True:
            current_time = datetime.now()
            for node_id, node in list(self.nodes.items()):
                if node.last_heartbeat:
                    time_since_heartbeat = (
                        current_time - node.last_heartbeat
                    ).total_seconds()
                    if time_since_heartbeat > self.node_timeout:
                        self.logger.warning(f"Node {node_id} has timed out")
                        await self._handle_node_timeout(node_id)

            await asyncio.sleep(self.heartbeat_interval)

    async def _handle_node_timeout(self, node_id: str) -> None:
        """
        Handle a node timeout.

        Args:
            node_id: ID of the timed out node
        """
        if node_id in self.nodes:
            node = self.nodes[node_id]
            self.logger.warning(
                f"Node {node_id} at {node.host}:{node.port} has timed out"
            )

            # Attempt to reconnect
            try:
                # Placeholder for reconnection logic
                await self._attempt_reconnect(node)
            except Exception as e:
                self.logger.error(f"Failed to reconnect to node {node_id}: {str(e)}")
                del self.nodes[node_id]

    async def _attempt_reconnect(self, node: TestNode) -> None:
        """
        Attempt to reconnect to a node.

        Args:
            node: TestNode instance to reconnect to
        """
        # Placeholder for actual reconnection logic
        self.logger.info(f"Attempting to reconnect to node {node.id}")
        await asyncio.sleep(1)  # Simulate reconnection attempt

    def get_node_status(self, node_id: str) -> Optional[str]:
        """
        Get the status of a node.

        Args:
            node_id: ID of the node to check

        Returns:
            Current status of the node, or None if node not found
        """
        return self.nodes.get(node_id, {}).get("status")

    def get_available_nodes(self) -> Dict[str, TestNode]:
        """
        Get all available (non-timed-out) nodes.

        Returns:
            Dictionary of available nodes
        """
        current_time = datetime.now()
        return {
            node_id: node
            for node_id, node in self.nodes.items()
            if node.last_heartbeat
            and (current_time - node.last_heartbeat).total_seconds()
            <= self.node_timeout
        }
