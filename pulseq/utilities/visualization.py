from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class MetricsVisualizer:
    def __init__(self):
        self.default_layout = {
            "template": "plotly_dark",
            "font": {"family": "Arial, sans-serif"},
            "margin": {"l": 50, "r": 50, "t": 50, "b": 50},
        }

    def create_performance_heatmap(
        self, metrics_data: List[Dict[str, Any]]
    ) -> go.Figure:
        """Create a heatmap showing performance metrics over time."""
        df = pd.DataFrame(metrics_data)
        metrics = ["cpu_percent", "memory_percent", "network_latency", "js_heap_used"]

        # Normalize data to 0-1 range for heatmap
        for metric in metrics:
            if metric in df.columns:
                df[metric] = (df[metric] - df[metric].min()) / (
                    df[metric].max() - df[metric].min()
                )

        fig = go.Figure(
            data=go.Heatmap(
                z=df[metrics].values.T,
                x=df["timestamp"],
                y=metrics,
                colorscale="Viridis",
            )
        )

        fig.update_layout(
            title="Performance Metrics Heatmap",
            xaxis_title="Time",
            yaxis_title="Metric",
            **self.default_layout,
        )

        return fig

    def create_resource_timeline(self, metrics_data: List[Dict[str, Any]]) -> go.Figure:
        """Create a timeline of resource usage with anomaly highlighting."""
        df = pd.DataFrame(metrics_data)

        fig = go.Figure()

        # Add CPU usage line
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["cpu_percent"],
                name="CPU Usage",
                line=dict(color="#00ff00", width=2),
            )
        )

        # Add memory usage line
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["memory_percent"],
                name="Memory Usage",
                line=dict(color="#ff0000", width=2),
            )
        )

        # Highlight anomalies
        anomalies = df[df["cpu_percent"] > 80].index
        if len(anomalies) > 0:
            fig.add_trace(
                go.Scatter(
                    x=df.loc[anomalies, "timestamp"],
                    y=df.loc[anomalies, "cpu_percent"],
                    mode="markers",
                    name="CPU Anomalies",
                    marker=dict(color="yellow", size=10, symbol="star"),
                )
            )

        fig.update_layout(
            title="Resource Usage Timeline",
            xaxis_title="Time",
            yaxis_title="Usage (%)",
            **self.default_layout,
        )

        return fig

    def create_latency_distribution(
        self, metrics_data: List[Dict[str, Any]]
    ) -> go.Figure:
        """Create a violin plot showing latency distribution."""
        df = pd.DataFrame(metrics_data)

        fig = go.Figure()

        fig.add_trace(
            go.Violin(
                y=df["network_latency"],
                box_visible=True,
                line_color="#00ff00",
                meanline_visible=True,
                fillcolor="#00ff00",
                opacity=0.6,
                name="Latency Distribution",
            )
        )

        fig.update_layout(
            title="Network Latency Distribution",
            yaxis_title="Latency (ms)",
            **self.default_layout,
        )

        return fig

    def create_performance_radar(
        self, current_metrics: Dict[str, float], baseline_metrics: Dict[str, float]
    ) -> go.Figure:
        """Create a radar chart comparing current vs baseline performance."""
        metrics = [
            "cpu_percent",
            "memory_percent",
            "network_latency",
            "js_heap_used",
            "dom_depth",
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=[current_metrics.get(m, 0) for m in metrics],
                theta=metrics,
                fill="toself",
                name="Current",
            )
        )

        fig.add_trace(
            go.Scatterpolar(
                r=[baseline_metrics.get(m, 0) for m in metrics],
                theta=metrics,
                fill="toself",
                name="Baseline",
            )
        )

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Performance Radar Chart",
            **self.default_layout,
        )

        return fig

    def create_resource_usage_gauge(
        self, current_value: float, threshold: float, title: str
    ) -> go.Figure:
        """Create a gauge chart for resource usage visualization."""
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=current_value,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": title},
                gauge={
                    "axis": {"range": [None, 100]},
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": threshold,
                    },
                    "steps": [
                        {"range": [0, 50], "color": "lightgray"},
                        {"range": [50, 80], "color": "gray"},
                        {"range": [80, 100], "color": "darkred"},
                    ],
                },
            )
        )

        fig.update_layout(**self.default_layout)
        return fig

    def create_performance_summary(
        self, metrics_data: List[Dict[str, Any]]
    ) -> go.Figure:
        """Create a comprehensive performance summary dashboard."""
        df = pd.DataFrame(metrics_data)

        # Create subplots
        fig = go.Figure()

        # Timeline
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"], y=df["cpu_percent"], name="CPU Usage", yaxis="y1"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["memory_percent"],
                name="Memory Usage",
                yaxis="y2",
            )
        )

        # Add latency bars
        fig.add_trace(
            go.Bar(
                x=df["timestamp"],
                y=df["network_latency"],
                name="Network Latency",
                yaxis="y3",
            )
        )

        # Update layout with multiple y-axes
        fig.update_layout(
            title="Performance Summary Dashboard",
            yaxis=dict(title="CPU %", side="left"),
            yaxis2=dict(title="Memory %", side="right", overlaying="y"),
            yaxis3=dict(title="Latency (ms)", side="right", overlaying="y"),
            **self.default_layout,
        )

        return fig

    def save_visualization(self, fig: go.Figure, filename: str):
        """Save visualization to HTML file."""
        fig.write_html(filename)

    def generate_report(self, metrics_data: List[Dict[str, Any]], output_dir: str):
        """Generate a comprehensive performance report with all visualizations."""
        # Create visualizations
        heatmap = self.create_performance_heatmap(metrics_data)
        timeline = self.create_resource_timeline(metrics_data)
        latency = self.create_latency_distribution(metrics_data)
        summary = self.create_performance_summary(metrics_data)

        # Save individual visualizations
        heatmap.write_html(f"{output_dir}/heatmap.html")
        timeline.write_html(f"{output_dir}/timeline.html")
        latency.write_html(f"{output_dir}/latency.html")
        summary.write_html(f"{output_dir}/summary.html")

        # Create index.html with links to all visualizations
        index_html = """
        <html>
        <head>
            <title>Performance Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .report-link { display: block; margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>Performance Report</h1>
            <a class="report-link" href="heatmap.html">Performance Metrics Heatmap</a>
            <a class="report-link" href="timeline.html">Resource Usage Timeline</a>
            <a class="report-link" href="latency.html">Latency Distribution</a>
            <a class="report-link" href="summary.html">Performance Summary</a>
        </body>
        </html>
        """

        with open(f"{output_dir}/index.html", "w") as f:
            f.write(index_html)
