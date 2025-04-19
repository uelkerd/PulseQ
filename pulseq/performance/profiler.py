"""
Performance profiler for PulseQ framework.
"""

import time
import cProfile
import pstats
import io
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
from dataclasses import dataclass
import logging

@dataclass
class PerformanceMetrics:
    """Performance metrics for a test execution."""
    test_id: str
    node_id: str
    start_time: float
    end_time: float
    cpu_usage: float
    memory_usage: float
    network_latency: float
    queue_time: float
    execution_time: float

class PerformanceProfiler:
    """Profiles and optimizes test execution performance."""
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize the performance profiler.
        
        Args:
            log_level: Logging level for profiler output
        """
        self.logger = logging.getLogger("PerformanceProfiler")
        self.logger.setLevel(log_level)
        
        self.metrics: List[PerformanceMetrics] = []
        self.profiles: Dict[str, pstats.Stats] = {}
        self.optimization_history: List[Dict] = []
    
    def profile_function(self, func, *args, **kwargs) -> Tuple[float, pstats.Stats]:
        """Profile a function's execution.
        
        Args:
            func: Function to profile
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Tuple of execution time and profiling stats
        """
        pr = cProfile.Profile()
        pr.enable()
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        pr.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        
        return end_time - start_time, ps
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics for a test execution.
        
        Args:
            metrics: Performance metrics to record
        """
        self.metrics.append(metrics)
        self.logger.debug(f"Recorded metrics for test {metrics.test_id}")
    
    def analyze_distribution(self) -> Dict:
        """Analyze test distribution performance.
        
        Returns:
            Dictionary containing distribution analysis results
        """
        if not self.metrics:
            return {}
        
        # Calculate distribution metrics
        node_metrics = {}
        for metric in self.metrics:
            if metric.node_id not in node_metrics:
                node_metrics[metric.node_id] = {
                    'total_tests': 0,
                    'total_time': 0,
                    'queue_times': [],
                    'execution_times': []
                }
            
            node_metrics[metric.node_id]['total_tests'] += 1
            node_metrics[metric.node_id]['total_time'] += metric.execution_time
            node_metrics[metric.node_id]['queue_times'].append(metric.queue_time)
            node_metrics[metric.node_id]['execution_times'].append(metric.execution_time)
        
        # Calculate load balancing metrics
        load_metrics = {
            'node_count': len(node_metrics),
            'avg_tests_per_node': np.mean([m['total_tests'] for m in node_metrics.values()]),
            'std_tests_per_node': np.std([m['total_tests'] for m in node_metrics.values()]),
            'avg_queue_time': np.mean([np.mean(m['queue_times']) for m in node_metrics.values()]),
            'avg_execution_time': np.mean([np.mean(m['execution_times']) for m in node_metrics.values()])
        }
        
        return load_metrics
    
    def analyze_load_balancing(self) -> Dict:
        """Analyze load balancing performance.
        
        Returns:
            Dictionary containing load balancing analysis results
        """
        if not self.metrics:
            return {}
        
        # Calculate load distribution
        node_loads = {}
        for metric in self.metrics:
            if metric.node_id not in node_loads:
                node_loads[metric.node_id] = []
            node_loads[metric.node_id].append(metric.cpu_usage)
        
        # Calculate load balancing metrics
        load_metrics = {
            'node_count': len(node_loads),
            'avg_load': np.mean([np.mean(loads) for loads in node_loads.values()]),
            'std_load': np.std([np.mean(loads) for loads in node_loads.values()]),
            'max_load': max([np.max(loads) for loads in node_loads.values()]),
            'min_load': min([np.min(loads) for loads in node_loads.values()])
        }
        
        return load_metrics
    
    def optimize_distribution(self, current_strategy: str) -> Dict:
        """Optimize test distribution strategy.
        
        Args:
            current_strategy: Current distribution strategy
            
        Returns:
            Dictionary containing optimization recommendations
        """
        distribution_metrics = self.analyze_distribution()
        load_metrics = self.analyze_load_balancing()
        
        recommendations = {
            'current_strategy': current_strategy,
            'distribution_efficiency': distribution_metrics.get('std_tests_per_node', 0),
            'load_balance': load_metrics.get('std_load', 0),
            'recommendations': []
        }
        
        # Analyze and recommend optimizations
        if distribution_metrics['std_tests_per_node'] > 2:
            recommendations['recommendations'].append({
                'type': 'distribution',
                'priority': 'high',
                'message': 'High variance in test distribution. Consider implementing dynamic load balancing.',
                'suggestion': 'Implement weighted round-robin distribution based on node capabilities'
            })
        
        if load_metrics['std_load'] > 0.2:
            recommendations['recommendations'].append({
                'type': 'load_balancing',
                'priority': 'medium',
                'message': 'Uneven load distribution detected.',
                'suggestion': 'Implement adaptive load balancing with real-time node health monitoring'
            })
        
        if distribution_metrics['avg_queue_time'] > 1.0:
            recommendations['recommendations'].append({
                'type': 'queue_optimization',
                'priority': 'high',
                'message': 'High queue times detected.',
                'suggestion': 'Implement priority-based queue management and preemptive scheduling'
            })
        
        self.optimization_history.append({
            'timestamp': datetime.now(),
            'recommendations': recommendations
        })
        
        return recommendations
    
    def generate_optimization_report(self) -> str:
        """Generate optimization report.
        
        Returns:
            String containing optimization report
        """
        if not self.optimization_history:
            return "No optimization data available"
        
        report = ["PulseQ Performance Optimization Report"]
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("\nOptimization History:")
        
        for entry in self.optimization_history:
            report.append(f"\nTimestamp: {entry['timestamp']}")
            for rec in entry['recommendations']['recommendations']:
                report.append(f"\n{rec['type'].upper()} ({rec['priority']} priority):")
                report.append(f"Message: {rec['message']}")
                report.append(f"Suggestion: {rec['suggestion']}")
        
        return "\n".join(report)
    
    def get_performance_summary(self) -> Dict:
        """Get summary of performance metrics.
        
        Returns:
            Dictionary containing performance summary
        """
        if not self.metrics:
            return {}
        
        return {
            'total_tests': len(self.metrics),
            'avg_execution_time': np.mean([m.execution_time for m in self.metrics]),
            'avg_queue_time': np.mean([m.queue_time for m in self.metrics]),
            'avg_cpu_usage': np.mean([m.cpu_usage for m in self.metrics]),
            'avg_memory_usage': np.mean([m.memory_usage for m in self.metrics]),
            'avg_network_latency': np.mean([m.network_latency for m in self.metrics])
        }
    
    def clear_metrics(self):
        """Clear recorded metrics."""
        self.metrics.clear()
        self.profiles.clear()
        self.logger.info("Cleared all performance metrics") 