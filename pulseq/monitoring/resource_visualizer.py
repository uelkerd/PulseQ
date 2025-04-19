"""
Visualization module for resource metrics and edge cases.
"""

from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class ResourceVisualizer:
    """Visualizer for resource metrics and edge cases."""

    def __init__(self):
        """Initialize the resource visualizer."""
        self.figures = {}

    def create_resource_dashboard(
        self, metrics: Dict[str, Any], title: str = "Resource Metrics Dashboard"
    ) -> go.Figure:
        """Create a comprehensive dashboard for resource metrics.

        Args:
            metrics: Dictionary containing resource metrics
            title: Title for the dashboard

        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=4,
            cols=2,
            subplot_titles=(
                "CPU Usage",
                "Memory Usage",
                "Network Usage",
                "Disk I/O",
                "Resource Contention",
                "Error Rates",
                "Performance Metrics",
                "Recovery Analysis",
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "heatmap"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "scatter"}],
            ],
        )

        # CPU Usage
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[r["cpu_usage"] for r in metrics["resource_usage"]],
                name="CPU Usage",
                line=dict(color="red"),
            ),
            row=1,
            col=1,
        )

        # Memory Usage
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[r["memory_usage"] for r in metrics["resource_usage"]],
                name="Memory Usage",
                line=dict(color="blue"),
            ),
            row=1,
            col=2,
        )

        # Network Usage
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[r["network_usage"] for r in metrics["resource_usage"]],
                name="Network Usage",
                line=dict(color="green"),
            ),
            row=2,
            col=1,
        )

        # Disk I/O
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[r["disk_usage"] for r in metrics["resource_usage"]],
                name="Disk Usage",
                line=dict(color="purple"),
            ),
            row=2,
            col=2,
        )

        # Resource Contention Heatmap
        contention_data = np.array(
            [
                [
                    r["resource_components"].get("cpu_throttling", 0),
                    r["resource_components"].get("memory_fragmentation", 0),
                    r["resource_components"].get("bandwidth_throttling", 0),
                    r["resource_components"].get("io_queue_depth", 0) / 32,
                ]
                for r in metrics["resource_usage"]
            ]
        )
        fig.add_trace(
            go.Heatmap(
                z=contention_data.T,
                x=metrics["timestamp"],
                y=[
                    "CPU Throttling",
                    "Memory Fragmentation",
                    "Network Throttling",
                    "Disk Queue",
                ],
                colorscale="Viridis",
            ),
            row=3,
            col=1,
        )

        # Error Rates
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=metrics["error_rates"],
                name="Error Rate",
                line=dict(color="orange"),
            ),
            row=3,
            col=2,
        )

        # Performance Metrics
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[m["strategy.success_rate"] for m in metrics["performance_metrics"]],
                name="Success Rate",
                line=dict(color="blue"),
            ),
            row=4,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    m["strategy.load_balance_score"]
                    for m in metrics["performance_metrics"]
                ],
                name="Load Balance",
                line=dict(color="green"),
            ),
            row=4,
            col=1,
        )

        # Recovery Analysis
        if metrics["recovery_times"]:
            fig.add_trace(
                go.Scatter(
                    x=[metrics["timestamp"][-1]],
                    y=metrics["recovery_times"],
                    name="Recovery Time",
                    mode="markers",
                    marker=dict(size=10, color="red"),
                ),
                row=4,
                col=2,
            )

        fig.update_layout(height=1200, width=1200, title_text=title, showlegend=True)

        return fig

    def create_resource_contention_analysis(self, metrics: Dict[str, Any]) -> go.Figure:
        """Create a detailed analysis of resource contention.

        Args:
            metrics: Dictionary containing resource metrics

        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "CPU Contention",
                "Memory Contention",
                "Network Contention",
                "Disk Contention",
            ),
        )

        # CPU Contention
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    r["resource_components"].get("cpu_throttling", 0)
                    for r in metrics["resource_usage"]
                ],
                name="CPU Throttling",
                line=dict(color="red"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    r["resource_components"].get("thermal_throttling", 0)
                    for r in metrics["resource_usage"]
                ],
                name="Thermal Throttling",
                line=dict(color="orange"),
            ),
            row=1,
            col=1,
        )

        # Memory Contention
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    r["resource_components"].get("memory_fragmentation", 0)
                    for r in metrics["resource_usage"]
                ],
                name="Memory Fragmentation",
                line=dict(color="blue"),
            ),
            row=1,
            col=2,
        )
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    r["resource_components"].get("swap_usage", 0)
                    for r in metrics["resource_usage"]
                ],
                name="Swap Usage",
                line=dict(color="purple"),
            ),
            row=1,
            col=2,
        )

        # Network Contention
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    r["resource_components"].get("latency", 0)
                    for r in metrics["resource_usage"]
                ],
                name="Network Latency",
                line=dict(color="green"),
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    r["resource_components"].get("packet_loss", 0)
                    for r in metrics["resource_usage"]
                ],
                name="Packet Loss",
                line=dict(color="yellow"),
            ),
            row=2,
            col=1,
        )

        # Disk Contention
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    r["resource_components"].get("read_latency", 0)
                    for r in metrics["resource_usage"]
                ],
                name="Read Latency",
                line=dict(color="brown"),
            ),
            row=2,
            col=2,
        )
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    r["resource_components"].get("write_latency", 0)
                    for r in metrics["resource_usage"]
                ],
                name="Write Latency",
                line=dict(color="pink"),
            ),
            row=2,
            col=2,
        )

        fig.update_layout(
            height=800,
            width=1000,
            title_text="Resource Contention Analysis",
            showlegend=True,
        )

        return fig

    def create_performance_impact_analysis(self, metrics: Dict[str, Any]) -> go.Figure:
        """Create an analysis of performance impact during resource contention.

        Args:
            metrics: Dictionary containing resource metrics

        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=2, cols=1, subplot_titles=("Performance Metrics", "Resource Impact")
        )

        # Performance Metrics
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[m["strategy.success_rate"] for m in metrics["performance_metrics"]],
                name="Success Rate",
                line=dict(color="blue"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    m["strategy.load_balance_score"]
                    for m in metrics["performance_metrics"]
                ],
                name="Load Balance",
                line=dict(color="green"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[
                    m["strategy.resource_efficiency"]
                    for m in metrics["performance_metrics"]
                ],
                name="Resource Efficiency",
                line=dict(color="red"),
            ),
            row=1,
            col=1,
        )

        # Resource Impact
        resource_impact = np.array(
            [
                [r["cpu_usage"], r["memory_usage"], r["network_usage"], r["disk_usage"]]
                for r in metrics["resource_usage"]
            ]
        )
        fig.add_trace(
            go.Heatmap(
                z=resource_impact.T,
                x=metrics["timestamp"],
                y=["CPU", "Memory", "Network", "Disk"],
                colorscale="Viridis",
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            height=800,
            width=1000,
            title_text="Performance Impact Analysis",
            showlegend=True,
        )

        return fig

    def create_recovery_analysis(self, metrics: Dict[str, Any]) -> go.Figure:
        """Create an analysis of system recovery patterns.

        Args:
            metrics: Dictionary containing resource metrics

        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=2, cols=1, subplot_titles=("Recovery Pattern", "Resource Recovery")
        )

        # Recovery Pattern
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[m["strategy.success_rate"] for m in metrics["performance_metrics"]],
                name="Success Rate",
                line=dict(color="blue"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=metrics["error_rates"],
                name="Error Rate",
                line=dict(color="red"),
            ),
            row=1,
            col=1,
        )

        # Resource Recovery
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[r["cpu_usage"] for r in metrics["resource_usage"]],
                name="CPU Recovery",
                line=dict(color="red"),
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[r["memory_usage"] for r in metrics["resource_usage"]],
                name="Memory Recovery",
                line=dict(color="blue"),
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=metrics["timestamp"],
                y=[r["network_usage"] for r in metrics["resource_usage"]],
                name="Network Recovery",
                line=dict(color="green"),
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            height=800, width=1000, title_text="Recovery Analysis", showlegend=True
        )

        return fig

    def save_visualizations(self, metrics: Dict[str, Any], output_dir: str):
        """Save all visualizations to HTML files.

        Args:
            metrics: Dictionary containing resource metrics
            output_dir: Directory to save the visualizations
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create and save dashboard
        dashboard = self.create_resource_dashboard(metrics)
        dashboard.write_html(f"{output_dir}/resource_dashboard_{timestamp}.html")

        # Create and save contention analysis
        contention = self.create_resource_contention_analysis(metrics)
        contention.write_html(f"{output_dir}/resource_contention_{timestamp}.html")

        # Create and save performance impact analysis
        performance = self.create_performance_impact_analysis(metrics)
        performance.write_html(f"{output_dir}/performance_impact_{timestamp}.html")

        # Create and save recovery analysis
        recovery = self.create_recovery_analysis(metrics)
        recovery.write_html(f"{output_dir}/recovery_analysis_{timestamp}.html")
