"""
Optimized load balancer for PulseQ framework.
"""

from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from .performance.profiler import PerformanceProfiler
import statistics

@dataclass
class NodeLoad:
    """Node load information."""
    node_id: str
    current_load: float
    cpu_usage: float
    memory_usage: float
    network_latency: float
    capabilities: Dict[str, str]
    last_update: datetime
    active_connections: int = 0
    response_times: List[float] = None
    predicted_load: float = 0.0

    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []

@dataclass
class NodeMetrics:
    """Detailed node performance metrics."""
    node_id: str
    timestamp: datetime
    current_load: float
    cpu_usage: float
    memory_usage: float
    network_latency: float
    active_connections: int
    avg_response_time: float
    predicted_load: float
    weight: float
    strategy_effectiveness: float = 0.0
    resource_utilization: float = 0.0
    queue_length: int = 0
    error_rate: float = 0.0
    health_score: float = 1.0

@dataclass
class StrategyMetrics:
    """Strategy-specific performance metrics."""
    strategy: str
    timestamp: datetime
    avg_selection_time: float
    success_rate: float
    load_balance_score: float
    resource_efficiency: float
    error_rate: float
    node_utilization: Dict[str, float]
    transition_count: int = 0
    last_transition_time: Optional[datetime] = None

class OptimizedLoadBalancer:
    """Optimized load balancer with performance profiling."""
    
    def __init__(self, profiler: Optional[PerformanceProfiler] = None):
        """Initialize the load balancer.
        
        Args:
            profiler: Optional performance profiler instance
        """
        self.logger = logging.getLogger("OptimizedLoadBalancer")
        self.nodes: Dict[str, NodeLoad] = {}
        self.profiler = profiler or PerformanceProfiler()
        self.strategy = "weighted_round_robin"
        self.weights: Dict[str, float] = {}
        self.update_interval = 5  # seconds
        self.response_time_window = 100  # number of samples to consider
        self.prediction_window = 10  # seconds for load prediction
        
        # Enhanced monitoring
        self.node_metrics_history: Dict[str, List[NodeMetrics]] = {}
        self.strategy_metrics_history: List[StrategyMetrics] = []
        self.selection_times: List[float] = []
        self.error_counts: Dict[str, int] = {}
        self.last_metrics_update = datetime.now()
    
    def add_node(self, node_id: str, capabilities: Dict[str, str]):
        """Add a node to the load balancer.
        
        Args:
            node_id: Node identifier
            capabilities: Node capabilities
        """
        self.nodes[node_id] = NodeLoad(
            node_id=node_id,
            current_load=0.0,
            cpu_usage=0.0,
            memory_usage=0.0,
            network_latency=0.0,
            capabilities=capabilities,
            last_update=datetime.now()
        )
        self._update_weights()
        self.logger.info(f"Added node {node_id} to load balancer")
    
    def remove_node(self, node_id: str):
        """Remove a node from the load balancer.
        
        Args:
            node_id: Node identifier
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
            self._update_weights()
            self.logger.info(f"Removed node {node_id} from load balancer")
    
    def update_node_load(self, node_id: str, load_info: Dict):
        """Update node load information.
        
        Args:
            node_id: Node identifier
            load_info: Dictionary containing load metrics
        """
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.current_load = load_info.get('current_load', node.current_load)
            node.cpu_usage = load_info.get('cpu_usage', node.cpu_usage)
            node.memory_usage = load_info.get('memory_usage', node.memory_usage)
            node.network_latency = load_info.get('network_latency', node.network_latency)
            node.active_connections = load_info.get('active_connections', node.active_connections)
            
            # Update response time history
            if 'response_time' in load_info:
                node.response_times.append(load_info['response_time'])
                if len(node.response_times) > self.response_time_window:
                    node.response_times.pop(0)
            
            node.last_update = datetime.now()
            self._update_weights()
    
    def _update_weights(self):
        """Update node weights based on current load and capabilities."""
        if not self.nodes:
            return
        
        # Calculate base weights from capabilities
        capability_weights = {
            node_id: self._calculate_capability_weight(node.capabilities)
            for node_id, node in self.nodes.items()
        }
        
        # Calculate load-based weights
        load_weights = {
            node_id: 1.0 / (node.current_load + 0.1)  # Add small constant to avoid division by zero
            for node_id, node in self.nodes.items()
        }
        
        # Combine weights
        total_weight = sum(capability_weights.values())
        if total_weight > 0:
            self.weights = {
                node_id: (capability_weights[node_id] * load_weights[node_id]) / total_weight
                for node_id in self.nodes
            }
        else:
            self.weights = {node_id: 1.0 / len(self.nodes) for node_id in self.nodes}
    
    def _calculate_capability_weight(self, capabilities: Dict[str, str]) -> float:
        """Calculate weight based on node capabilities.
        
        Args:
            capabilities: Node capabilities
            
        Returns:
            Capability weight
        """
        weight = 1.0
        
        # Adjust weight based on capabilities
        if capabilities.get('os') == 'linux':
            weight *= 1.2  # Linux nodes get higher weight
        
        if capabilities.get('memory', '8GB') == '16GB':
            weight *= 1.5  # Higher memory nodes get higher weight
        
        if capabilities.get('cpu_cores', '4') == '8':
            weight *= 1.3  # More CPU cores get higher weight
        
        return weight
    
    def select_node(self, test_requirements: Optional[Dict] = None) -> Optional[str]:
        """Select a node for test execution.
        
        Args:
            test_requirements: Optional test requirements
            
        Returns:
            Selected node ID or None if no suitable node found
        """
        if not self.nodes:
            return None
        
        # Filter nodes based on requirements
        suitable_nodes = self._filter_nodes_by_requirements(test_requirements)
        if not suitable_nodes:
            return None
        
        # Select node based on strategy
        if self.strategy == "weighted_round_robin":
            return self._weighted_round_robin(suitable_nodes)
        elif self.strategy == "least_load":
            return self._least_load(suitable_nodes)
        elif self.strategy == "least_connections":
            return self._least_connections(suitable_nodes)
        elif self.strategy == "response_time":
            return self._response_time_based(suitable_nodes)
        elif self.strategy == "predictive":
            return self._predictive_load(suitable_nodes)
        else:
            return self._weighted_round_robin(suitable_nodes)
    
    def _filter_nodes_by_requirements(self, requirements: Optional[Dict]) -> List[str]:
        """Filter nodes based on test requirements.
        
        Args:
            requirements: Test requirements
            
        Returns:
            List of suitable node IDs
        """
        if not requirements:
            return list(self.nodes.keys())
        
        suitable_nodes = []
        for node_id, node in self.nodes.items():
            if all(
                node.capabilities.get(key) == value
                for key, value in requirements.items()
            ):
                suitable_nodes.append(node_id)
        
        return suitable_nodes
    
    def _weighted_round_robin(self, nodes: List[str]) -> str:
        """Select node using weighted round-robin strategy.
        
        Args:
            nodes: List of suitable node IDs
            
        Returns:
            Selected node ID
        """
        if not nodes:
            return None
        
        # Calculate total weight for selected nodes
        total_weight = sum(self.weights[node_id] for node_id in nodes)
        if total_weight <= 0:
            return nodes[0]
        
        # Select node based on weights
        selection = np.random.random() * total_weight
        current_sum = 0
        for node_id in nodes:
            current_sum += self.weights[node_id]
            if selection <= current_sum:
                return node_id
        
        return nodes[-1]
    
    def _least_load(self, nodes: List[str]) -> str:
        """Select node with least current load.
        
        Args:
            nodes: List of suitable node IDs
            
        Returns:
            Selected node ID
        """
        if not nodes:
            return None
        
        return min(
            nodes,
            key=lambda node_id: self.nodes[node_id].current_load
        )
    
    def _least_connections(self, nodes: List[str]) -> str:
        """Select node with least active connections.
        
        Args:
            nodes: List of suitable node IDs
            
        Returns:
            Selected node ID
        """
        if not nodes:
            return None
        
        return min(
            nodes,
            key=lambda node_id: self.nodes[node_id].active_connections
        )
    
    def _response_time_based(self, nodes: List[str]) -> str:
        """Select node based on response time history.
        
        Args:
            nodes: List of suitable node IDs
            
        Returns:
            Selected node ID
        """
        if not nodes:
            return None
        
        def get_avg_response_time(node_id: str) -> float:
            node = self.nodes[node_id]
            if not node.response_times:
                return float('inf')
            return statistics.mean(node.response_times[-self.response_time_window:])
        
        return min(nodes, key=get_avg_response_time)
    
    def _predictive_load(self, nodes: List[str]) -> str:
        """Select node based on predicted future load.
        
        Args:
            nodes: List of suitable node IDs
            
        Returns:
            Selected node ID
        """
        if not nodes:
            return None
        
        # Update predictions for all nodes
        for node_id in nodes:
            self._update_predicted_load(node_id)
        
        return min(
            nodes,
            key=lambda node_id: self.nodes[node_id].predicted_load
        )
    
    def _update_predicted_load(self, node_id: str):
        """Update predicted load for a node.
        
        Args:
            node_id: Node identifier
        """
        node = self.nodes[node_id]
        
        # Calculate load trend
        recent_loads = [
            self.profiler.get_node_load(node_id, t)
            for t in range(self.prediction_window)
        ]
        
        if len(recent_loads) > 1:
            # Simple linear regression for prediction
            x = np.arange(len(recent_loads))
            y = np.array(recent_loads)
            slope, _ = np.polyfit(x, y, 1)
            
            # Predict load based on trend
            node.predicted_load = node.current_load + slope * self.prediction_window
        else:
            node.predicted_load = node.current_load
    
    def optimize_strategy(self):
        """Optimize load balancing strategy based on performance metrics."""
        if not self.profiler:
            return
        
        # Get optimization recommendations
        recommendations = self.profiler.optimize_distribution(self.strategy)
        
        # Apply recommendations
        for rec in recommendations['recommendations']:
            if rec['type'] == 'load_balancing' and rec['priority'] == 'high':
                if rec['suggestion'] == 'least_connections':
                    self.strategy = "least_connections"
                    self.logger.info("Switched to least-connections strategy based on optimization")
                elif rec['suggestion'] == 'response_time':
                    self.strategy = "response_time"
                    self.logger.info("Switched to response-time strategy based on optimization")
                elif rec['suggestion'] == 'predictive':
                    self.strategy = "predictive"
                    self.logger.info("Switched to predictive strategy based on optimization")
                else:
                    self.strategy = "least_load"
                    self.logger.info("Switched to least-load strategy based on optimization")
            elif rec['type'] == 'distribution' and rec['priority'] == 'high':
                self.strategy = "weighted_round_robin"
                self.logger.info("Switched to weighted round-robin strategy based on optimization")
    
    def get_node_stats(self) -> Dict:
        """Get current node statistics.
        
        Returns:
            Dictionary containing node statistics
        """
        return {
            node_id: {
                'current_load': node.current_load,
                'cpu_usage': node.cpu_usage,
                'memory_usage': node.memory_usage,
                'network_latency': node.network_latency,
                'active_connections': node.active_connections,
                'avg_response_time': statistics.mean(node.response_times) if node.response_times else 0,
                'predicted_load': node.predicted_load,
                'weight': self.weights.get(node_id, 0.0)
            }
            for node_id, node in self.nodes.items()
        }

    def _update_node_metrics(self, node_id: str):
        """Update detailed metrics for a node.
        
        Args:
            node_id: Node identifier
        """
        node = self.nodes[node_id]
        
        # Calculate resource utilization
        resource_utilization = (node.cpu_usage + node.memory_usage) / 2
        
        # Calculate health score
        health_score = 1.0
        if node.current_load > 0.9:
            health_score *= 0.5
        if node.cpu_usage > 0.9:
            health_score *= 0.7
        if node.memory_usage > 0.9:
            health_score *= 0.7
        if node.network_latency > 0.5:
            health_score *= 0.8
        
        # Calculate strategy effectiveness
        strategy_effectiveness = 1.0
        if self.strategy == "least_connections":
            strategy_effectiveness = 1.0 - (node.active_connections / 100)  # Assuming max 100 connections
        elif self.strategy == "response_time":
            avg_response = statistics.mean(node.response_times) if node.response_times else 0
            strategy_effectiveness = 1.0 - min(1.0, avg_response)
        elif self.strategy == "predictive":
            strategy_effectiveness = 1.0 - abs(node.current_load - node.predicted_load)
        
        metrics = NodeMetrics(
            node_id=node_id,
            timestamp=datetime.now(),
            current_load=node.current_load,
            cpu_usage=node.cpu_usage,
            memory_usage=node.memory_usage,
            network_latency=node.network_latency,
            active_connections=node.active_connections,
            avg_response_time=statistics.mean(node.response_times) if node.response_times else 0,
            predicted_load=node.predicted_load,
            weight=self.weights.get(node_id, 0.0),
            strategy_effectiveness=strategy_effectiveness,
            resource_utilization=resource_utilization,
            queue_length=node.active_connections,
            health_score=health_score
        )
        
        if node_id not in self.node_metrics_history:
            self.node_metrics_history[node_id] = []
        self.node_metrics_history[node_id].append(metrics)
        
        # Keep only last 1000 metrics per node
        if len(self.node_metrics_history[node_id]) > 1000:
            self.node_metrics_history[node_id].pop(0)

    def _update_strategy_metrics(self):
        """Update strategy-specific performance metrics."""
        now = datetime.now()
        
        # Calculate average selection time
        avg_selection_time = statistics.mean(self.selection_times) if self.selection_times else 0
        
        # Calculate success rate
        total_selections = len(self.selection_times)
        successful_selections = total_selections - sum(self.error_counts.values())
        success_rate = successful_selections / total_selections if total_selections > 0 else 1.0
        
        # Calculate load balance score
        node_loads = [node.current_load for node in self.nodes.values()]
        load_balance_score = 1.0 - statistics.stdev(node_loads) if len(node_loads) > 1 else 1.0
        
        # Calculate resource efficiency
        resource_efficiencies = [
            metrics.resource_utilization for metrics_list in self.node_metrics_history.values()
            for metrics in metrics_list[-10:]  # Last 10 metrics
        ]
        resource_efficiency = statistics.mean(resource_efficiencies) if resource_efficiencies else 0
        
        # Calculate error rate
        total_errors = sum(self.error_counts.values())
        error_rate = total_errors / total_selections if total_selections > 0 else 0
        
        # Calculate node utilization
        node_utilization = {
            node_id: statistics.mean([m.resource_utilization for m in metrics[-10:]])
            for node_id, metrics in self.node_metrics_history.items()
        }
        
        # Get transition information
        transition_count = 0
        last_transition_time = None
        if len(self.strategy_metrics_history) > 0:
            last_metrics = self.strategy_metrics_history[-1]
            if last_metrics.strategy != self.strategy:
                transition_count = last_metrics.transition_count + 1
                last_transition_time = now
        
        metrics = StrategyMetrics(
            strategy=self.strategy,
            timestamp=now,
            avg_selection_time=avg_selection_time,
            success_rate=success_rate,
            load_balance_score=load_balance_score,
            resource_efficiency=resource_efficiency,
            error_rate=error_rate,
            node_utilization=node_utilization,
            transition_count=transition_count,
            last_transition_time=last_transition_time
        )
        
        self.strategy_metrics_history.append(metrics)
        
        # Keep only last 1000 strategy metrics
        if len(self.strategy_metrics_history) > 1000:
            self.strategy_metrics_history.pop(0)
        
        # Clear selection times and error counts
        self.selection_times.clear()
        self.error_counts.clear()

    def get_detailed_metrics(self) -> Dict:
        """Get detailed performance metrics.
        
        Returns:
            Dictionary containing detailed metrics
        """
        # Update metrics if needed
        if (datetime.now() - self.last_metrics_update).total_seconds() >= self.update_interval:
            for node_id in self.nodes:
                self._update_node_metrics(node_id)
            self._update_strategy_metrics()
            self.last_metrics_update = datetime.now()
        
        # Get latest metrics
        latest_node_metrics = {
            node_id: metrics[-1] if metrics else None
            for node_id, metrics in self.node_metrics_history.items()
        }
        
        latest_strategy_metrics = self.strategy_metrics_history[-1] if self.strategy_metrics_history else None
        
        return {
            "nodes": {
                node_id: {
                    "current_load": metrics.current_load,
                    "cpu_usage": metrics.cpu_usage,
                    "memory_usage": metrics.memory_usage,
                    "network_latency": metrics.network_latency,
                    "active_connections": metrics.active_connections,
                    "avg_response_time": metrics.avg_response_time,
                    "predicted_load": metrics.predicted_load,
                    "weight": metrics.weight,
                    "strategy_effectiveness": metrics.strategy_effectiveness,
                    "resource_utilization": metrics.resource_utilization,
                    "queue_length": metrics.queue_length,
                    "error_rate": metrics.error_rate,
                    "health_score": metrics.health_score
                }
                for node_id, metrics in latest_node_metrics.items()
                if metrics is not None
            },
            "strategy": {
                "current": self.strategy,
                "avg_selection_time": latest_strategy_metrics.avg_selection_time if latest_strategy_metrics else 0,
                "success_rate": latest_strategy_metrics.success_rate if latest_strategy_metrics else 1.0,
                "load_balance_score": latest_strategy_metrics.load_balance_score if latest_strategy_metrics else 1.0,
                "resource_efficiency": latest_strategy_metrics.resource_efficiency if latest_strategy_metrics else 0,
                "error_rate": latest_strategy_metrics.error_rate if latest_strategy_metrics else 0,
                "transition_count": latest_strategy_metrics.transition_count if latest_strategy_metrics else 0,
                "last_transition_time": latest_strategy_metrics.last_transition_time if latest_strategy_metrics else None
            } if latest_strategy_metrics else None
        } 