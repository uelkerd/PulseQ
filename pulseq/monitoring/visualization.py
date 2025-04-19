"""
Visualization module for load balancer metrics.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss, grangercausalitytests
from scipy.stats import norm, kurtosis, skew, chi2_contingency, mannwhitneyu, kruskal
from statsmodels.stats.power import tt_ind_solve_power
from statsmodels.stats.multitest import multipletests
import warnings
warnings.filterwarnings('ignore')

class LoadBalancerVisualizer:
    """Visualization tools for load balancer metrics."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.color_palette = {
            "weighted_round_robin": "#1f77b4",
            "least_connections": "#ff7f0e",
            "response_time": "#2ca02c",
            "predictive": "#d62728"
        }
    
    def create_performance_dashboard(self, metrics_history: List[Dict]) -> go.Figure:
        """Create a comprehensive performance dashboard.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the dashboard
        """
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "Strategy Performance Over Time",
                "Node Load Distribution",
                "Resource Utilization",
                "Success Rate & Error Rate",
                "Load Balance Score",
                "Transition Impact"
            )
        )
        
        # Convert metrics to DataFrame
        df = pd.DataFrame(metrics_history)
        
        # Strategy Performance Over Time
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["strategy.avg_selection_time"] * 1000,
                name="Selection Time (ms)",
                line=dict(color=self.color_palette[df["strategy.current"].iloc[0]])
            ),
            row=1, col=1
        )
        
        # Node Load Distribution
        node_loads = pd.DataFrame(df["nodes"].tolist())
        fig.add_trace(
            go.Box(
                y=[loads["current_load"] for loads in node_loads.values.flatten()],
                name="Load Distribution",
                boxpoints="all",
                jitter=0.3,
                pointpos=-1.8
            ),
            row=1, col=2
        )
        
        # Resource Utilization
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["strategy.resource_efficiency"] * 100,
                name="Resource Efficiency (%)",
                line=dict(color="#9467bd")
            ),
            row=2, col=1
        )
        
        # Success Rate & Error Rate
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["strategy.success_rate"] * 100,
                name="Success Rate (%)",
                line=dict(color="#2ca02c")
            ),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["strategy.error_rate"] * 100,
                name="Error Rate (%)",
                line=dict(color="#d62728")
            ),
            row=2, col=2
        )
        
        # Load Balance Score
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["strategy.load_balance_score"] * 100,
                name="Load Balance Score (%)",
                line=dict(color="#ff7f0e")
            ),
            row=3, col=1
        )
        
        # Transition Impact
        transitions = df[df["strategy.transition_count"].diff() > 0]
        if not transitions.empty:
            fig.add_trace(
                go.Scatter(
                    x=transitions.index,
                    y=transitions["strategy.avg_selection_time"] * 1000,
                    mode="markers",
                    name="Transition Points",
                    marker=dict(
                        size=10,
                        color="#e377c2",
                        symbol="star"
                    )
                ),
                row=3, col=2
            )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="Load Balancer Performance Dashboard",
            showlegend=True
        )
        
        return fig
    
    def create_node_health_heatmap(self, metrics_history: List[Dict]) -> go.Figure:
        """Create a heatmap of node health metrics.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the heatmap
        """
        # Extract node metrics
        node_metrics = []
        for metrics in metrics_history:
            for node_id, node_data in metrics["nodes"].items():
                node_metrics.append({
                    "timestamp": metrics["timestamp"],
                    "node_id": node_id,
                    "health_score": node_data["health_score"],
                    "resource_utilization": node_data["resource_utilization"],
                    "strategy_effectiveness": node_data["strategy_effectiveness"]
                })
        
        df = pd.DataFrame(node_metrics)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=df.pivot(index="timestamp", columns="node_id", values="health_score"),
            x=df["node_id"].unique(),
            y=df["timestamp"],
            colorscale="RdYlGn",
            zmin=0,
            zmax=1
        ))
        
        fig.update_layout(
            title="Node Health Heatmap",
            xaxis_title="Node ID",
            yaxis_title="Time",
            height=600
        )
        
        return fig
    
    def create_strategy_comparison(self, metrics_history: List[Dict]) -> go.Figure:
        """Create a comparison of different strategies.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the comparison
        """
        # Group metrics by strategy
        df = pd.DataFrame(metrics_history)
        strategy_groups = df.groupby("strategy.current")
        
        # Create radar chart
        fig = go.Figure()
        
        metrics = [
            "strategy.avg_selection_time",
            "strategy.success_rate",
            "strategy.load_balance_score",
            "strategy.resource_efficiency"
        ]
        
        for strategy, group in strategy_groups:
            values = [
                group[metric].mean()
                for metric in metrics
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metrics,
                fill="toself",
                name=strategy,
                line_color=self.color_palette[strategy]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="Strategy Performance Comparison",
            showlegend=True
        )
        
        return fig
    
    def create_transition_analysis(self, metrics_history: List[Dict]) -> go.Figure:
        """Create an analysis of strategy transitions.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the analysis
        """
        df = pd.DataFrame(metrics_history)
        transitions = df[df["strategy.transition_count"].diff() > 0]
        
        if transitions.empty:
            return None
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(
                "Transition Impact on Performance",
                "Transition Recovery Time"
            )
        )
        
        # Transition Impact
        for metric in ["avg_selection_time", "success_rate", "load_balance_score"]:
            fig.add_trace(
                go.Scatter(
                    x=transitions.index,
                    y=transitions[f"strategy.{metric}"] * (1000 if metric == "avg_selection_time" else 100),
                    name=metric.replace("_", " ").title(),
                    mode="lines+markers"
                ),
                row=1, col=1
            )
        
        # Recovery Time
        recovery_times = []
        for idx in transitions.index:
            pre_transition = df.loc[:idx-1].iloc[-5:]  # Last 5 points before transition
            post_transition = df.loc[idx:].iloc[:10]   # First 10 points after transition
            
            if len(pre_transition) > 0 and len(post_transition) > 0:
                baseline = pre_transition["strategy.avg_selection_time"].mean()
                recovery_idx = next(
                    (i for i, val in enumerate(post_transition["strategy.avg_selection_time"])
                     if abs(val - baseline) / baseline < 0.1),
                    len(post_transition)
                )
                recovery_times.append(recovery_idx)
        
        fig.add_trace(
            go.Histogram(
                x=recovery_times,
                name="Recovery Time Distribution",
                nbinsx=10
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=800,
            title_text="Strategy Transition Analysis",
            showlegend=True
        )
        
        return fig
    
    def create_correlation_analysis(self, metrics_history: List[Dict]) -> go.Figure:
        """Create a correlation analysis visualization.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the correlation analysis
        """
        # Convert metrics to DataFrame
        df = pd.DataFrame(metrics_history)
        
        # Extract relevant metrics
        metrics = [
            "strategy.avg_selection_time",
            "strategy.success_rate",
            "strategy.load_balance_score",
            "strategy.resource_efficiency",
            "strategy.error_rate"
        ]
        
        # Calculate correlation matrix
        correlation_matrix = df[metrics].corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=metrics,
            y=metrics,
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
            text=correlation_matrix.round(2),
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Metric Correlation Analysis",
            xaxis_title="Metrics",
            yaxis_title="Metrics",
            height=600
        )
        
        return fig
    
    def create_trend_prediction(self, metrics_history: List[Dict], metric: str, steps: int = 10) -> go.Figure:
        """Create a trend prediction visualization.
        
        Args:
            metrics_history: List of metrics dictionaries
            metric: Metric to predict
            steps: Number of future steps to predict
            
        Returns:
            Plotly figure containing the trend prediction
        """
        df = pd.DataFrame(metrics_history)
        
        # Prepare data for prediction
        X = np.array(range(len(df))).reshape(-1, 1)
        y = df[metric].values
        
        # Create polynomial features
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        
        # Fit model
        model = LinearRegression()
        model.fit(X_poly, y)
        
        # Generate predictions
        future_X = np.array(range(len(df) + steps)).reshape(-1, 1)
        future_X_poly = poly.transform(future_X)
        predictions = model.predict(future_X_poly)
        
        # Create figure
        fig = go.Figure()
        
        # Add actual data
        fig.add_trace(go.Scatter(
            x=df.index,
            y=y,
            name="Actual",
            line=dict(color=self.color_palette[df["strategy.current"].iloc[0]])
        ))
        
        # Add predictions
        fig.add_trace(go.Scatter(
            x=list(range(len(df), len(df) + steps)),
            y=predictions[-steps:],
            name="Predicted",
            line=dict(color="#ff7f0e", dash="dash")
        ))
        
        # Add confidence interval
        y_err = np.std(y) * 1.96  # 95% confidence interval
        fig.add_trace(go.Scatter(
            x=list(range(len(df), len(df) + steps)),
            y=predictions[-steps:] + y_err,
            name="Upper Bound",
            line=dict(color="rgba(255,127,14,0.2)"),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=list(range(len(df), len(df) + steps)),
            y=predictions[-steps:] - y_err,
            name="Lower Bound",
            line=dict(color="rgba(255,127,14,0.2)"),
            fill="tonexty",
            showlegend=False
        ))
        
        fig.update_layout(
            title=f"Trend Prediction for {metric}",
            xaxis_title="Time",
            yaxis_title="Value",
            height=600
        )
        
        return fig
    
    def create_workload_pattern_analysis(self, metrics_history: List[Dict]) -> go.Figure:
        """Create a workload pattern analysis visualization.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the workload pattern analysis
        """
        df = pd.DataFrame(metrics_history)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Load Distribution Over Time",
                "Resource Usage Patterns",
                "Connection Patterns",
                "Response Time Distribution"
            )
        )
        
        # Load Distribution
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["strategy.load_balance_score"],
                name="Load Balance Score",
                line=dict(color="#1f77b4")
            ),
            row=1, col=1
        )
        
        # Resource Usage
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["strategy.resource_efficiency"],
                name="Resource Efficiency",
                line=dict(color="#2ca02c")
            ),
            row=1, col=2
        )
        
        # Connection Patterns
        node_metrics = pd.DataFrame(df["nodes"].tolist())
        avg_connections = [
            np.mean([node["active_connections"] for node in nodes.values()])
            for nodes in node_metrics.values
        ]
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=avg_connections,
                name="Average Connections",
                line=dict(color="#ff7f0e")
            ),
            row=2, col=1
        )
        
        # Response Time Distribution
        response_times = [
            np.mean([node["avg_response_time"] for node in nodes.values()])
            for nodes in node_metrics.values
        ]
        fig.add_trace(
            go.Histogram(
                x=response_times,
                name="Response Time Distribution",
                nbinsx=20
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Workload Pattern Analysis",
            showlegend=True
        )
        
        return fig
    
    def create_strategy_effectiveness_matrix(self, metrics_history: List[Dict]) -> go.Figure:
        """Create a strategy effectiveness matrix visualization.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the strategy effectiveness matrix
        """
        df = pd.DataFrame(metrics_history)
        
        # Group metrics by strategy
        strategy_groups = df.groupby("strategy.current")
        
        # Calculate effectiveness metrics
        effectiveness_metrics = []
        for strategy, group in strategy_groups:
            effectiveness_metrics.append({
                "strategy": strategy,
                "avg_selection_time": group["strategy.avg_selection_time"].mean(),
                "success_rate": group["strategy.success_rate"].mean(),
                "load_balance": group["strategy.load_balance_score"].mean(),
                "resource_efficiency": group["strategy.resource_efficiency"].mean()
            })
        
        effectiveness_df = pd.DataFrame(effectiveness_metrics)
        
        # Create matrix
        fig = go.Figure(data=go.Heatmap(
            z=effectiveness_df.drop("strategy", axis=1).values,
            x=effectiveness_df.columns[1:],
            y=effectiveness_df["strategy"],
            colorscale="RdYlGn",
            text=effectiveness_df.drop("strategy", axis=1).round(2),
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Strategy Effectiveness Matrix",
            xaxis_title="Metrics",
            yaxis_title="Strategy",
            height=400
        )
        
        return fig
    
    def create_statistical_analysis(self, metrics_history: List[Dict]) -> go.Figure:
        """Create a comprehensive statistical analysis visualization.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the statistical analysis
        """
        df = pd.DataFrame(metrics_history)
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "Time Series Decomposition",
                "Distribution Analysis",
                "Autocorrelation Analysis",
                "Stationarity Test",
                "Outlier Detection",
                "Statistical Summary"
            )
        )
        
        # Time Series Decomposition
        metric = "strategy.avg_selection_time"
        decomposition = seasonal_decompose(df[metric], period=24)  # Assuming daily seasonality
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=decomposition.trend,
                name="Trend",
                line=dict(color="#1f77b4")
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=decomposition.seasonal,
                name="Seasonal",
                line=dict(color="#2ca02c")
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=decomposition.resid,
                name="Residual",
                line=dict(color="#d62728")
            ),
            row=1, col=1
        )
        
        # Distribution Analysis
        data = df[metric].values
        hist_data = go.Histogram(
            x=data,
            name="Distribution",
            nbinsx=30,
            histnorm="probability density"
        )
        fig.add_trace(hist_data, row=1, col=2)
        
        # Add normal distribution overlay
        x_range = np.linspace(min(data), max(data), 100)
        pdf = norm.pdf(x_range, np.mean(data), np.std(data))
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=pdf,
                name="Normal Distribution",
                line=dict(color="#ff7f0e")
            ),
            row=1, col=2
        )
        
        # Autocorrelation Analysis
        autocorr = [df[metric].autocorr(lag=i) for i in range(1, 31)]
        fig.add_trace(
            go.Bar(
                x=list(range(1, 31)),
                y=autocorr,
                name="Autocorrelation",
                marker_color="#9467bd"
            ),
            row=2, col=1
        )
        
        # Stationarity Test
        adf_result = adfuller(df[metric])
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=adf_result[0],
                title={"text": "ADF Test Statistic"},
                gauge={"axis": {"range": [-5, 5]}},
                domain={"row": 1, "column": 1}
            ),
            row=2, col=2
        )
        
        # Outlier Detection
        z_scores = np.abs(stats.zscore(data))
        outliers = data[z_scores > 3]
        fig.add_trace(
            go.Scatter(
                x=df.index[z_scores > 3],
                y=outliers,
                mode="markers",
                name="Outliers",
                marker=dict(
                    color="red",
                    size=10,
                    symbol="x"
                )
            ),
            row=3, col=1
        )
        
        # Statistical Summary
        summary_stats = {
            "Mean": np.mean(data),
            "Median": np.median(data),
            "Std Dev": np.std(data),
            "Skewness": skew(data),
            "Kurtosis": kurtosis(data)
        }
        
        fig.add_trace(
            go.Table(
                header=dict(values=["Statistic", "Value"]),
                cells=dict(values=[
                    list(summary_stats.keys()),
                    [f"{v:.4f}" for v in summary_stats.values()]
                ])
            ),
            row=3, col=2
        )
        
        fig.update_layout(
            height=1200,
            title_text="Statistical Analysis",
            showlegend=True
        )
        
        return fig
    
    def create_performance_anomaly_detection(self, metrics_history: List[Dict]) -> go.Figure:
        """Create an anomaly detection visualization.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the anomaly detection analysis
        """
        df = pd.DataFrame(metrics_history)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(
                "Performance Metrics with Anomalies",
                "Anomaly Score Distribution"
            )
        )
        
        # Calculate anomaly scores using multiple methods
        metrics = [
            "strategy.avg_selection_time",
            "strategy.success_rate",
            "strategy.load_balance_score"
        ]
        
        for metric in metrics:
            # Z-score based anomaly detection
            z_scores = np.abs(stats.zscore(df[metric]))
            anomalies = z_scores > 3
            
            # Add metric trace
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[metric],
                    name=metric,
                    line=dict(color=self.color_palette[df["strategy.current"].iloc[0]])
                ),
                row=1, col=1
            )
            
            # Add anomaly markers
            fig.add_trace(
                go.Scatter(
                    x=df.index[anomalies],
                    y=df[metric][anomalies],
                    mode="markers",
                    name=f"{metric} Anomalies",
                    marker=dict(
                        color="red",
                        size=10,
                        symbol="x"
                    )
                ),
                row=1, col=1
            )
        
        # Anomaly score distribution
        fig.add_trace(
            go.Histogram(
                x=z_scores,
                name="Anomaly Score Distribution",
                nbinsx=30
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=800,
            title_text="Performance Anomaly Detection",
            showlegend=True
        )
        
        return fig
    
    def create_strategy_impact_analysis(self, metrics_history: List[Dict]) -> go.Figure:
        """Create a strategy impact analysis visualization.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the strategy impact analysis
        """
        df = pd.DataFrame(metrics_history)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Strategy Impact on Performance",
                "Strategy Transition Effects",
                "Strategy Effectiveness by Metric",
                "Strategy Stability Analysis"
            )
        )
        
        # Strategy Impact on Performance
        strategy_groups = df.groupby("strategy.current")
        for strategy, group in strategy_groups:
            fig.add_trace(
                go.Box(
                    y=group["strategy.avg_selection_time"],
                    name=strategy,
                    boxpoints="all",
                    jitter=0.3,
                    pointpos=-1.8,
                    marker_color=self.color_palette[strategy]
                ),
                row=1, col=1
            )
        
        # Strategy Transition Effects
        transitions = df[df["strategy.transition_count"].diff() > 0]
        if not transitions.empty:
            for metric in ["success_rate", "load_balance_score"]:
                fig.add_trace(
                    go.Scatter(
                        x=transitions.index,
                        y=transitions[f"strategy.{metric}"],
                        name=f"{metric.replace('_', ' ').title()}",
                        mode="lines+markers"
                    ),
                    row=1, col=2
                )
        
        # Strategy Effectiveness by Metric
        effectiveness = []
        for strategy, group in strategy_groups:
            effectiveness.append({
                "strategy": strategy,
                "selection_time": group["strategy.avg_selection_time"].mean(),
                "success_rate": group["strategy.success_rate"].mean(),
                "load_balance": group["strategy.load_balance_score"].mean()
            })
        
        effectiveness_df = pd.DataFrame(effectiveness)
        for metric in ["selection_time", "success_rate", "load_balance"]:
            fig.add_trace(
                go.Bar(
                    x=effectiveness_df["strategy"],
                    y=effectiveness_df[metric],
                    name=metric.replace("_", " ").title(),
                    marker_color=[self.color_palette[s] for s in effectiveness_df["strategy"]]
                ),
                row=2, col=1
            )
        
        # Strategy Stability Analysis
        stability = []
        for strategy, group in strategy_groups:
            stability.append({
                "strategy": strategy,
                "variance": group["strategy.avg_selection_time"].var(),
                "stability_score": 1 / (1 + group["strategy.avg_selection_time"].var())
            })
        
        stability_df = pd.DataFrame(stability)
        fig.add_trace(
            go.Bar(
                x=stability_df["strategy"],
                y=stability_df["stability_score"],
                name="Stability Score",
                marker_color=[self.color_palette[s] for s in stability_df["strategy"]]
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Strategy Impact Analysis",
            showlegend=True
        )
        
        return fig
    
    def create_advanced_statistical_analysis(self, metrics_history: List[Dict]) -> go.Figure:
        """Create an advanced statistical analysis visualization.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the advanced statistical analysis
        """
        df = pd.DataFrame(metrics_history)
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "Causality Analysis",
                "Power Analysis",
                "Multiple Comparison Tests",
                "Non-parametric Tests",
                "Time Series Stationarity",
                "Statistical Power"
            )
        )
        
        # Causality Analysis (Granger Causality)
        metrics = [
            "strategy.avg_selection_time",
            "strategy.success_rate",
            "strategy.load_balance_score"
        ]
        
        causality_results = []
        for i, metric1 in enumerate(metrics):
            for j, metric2 in enumerate(metrics):
                if i != j:
                    try:
                        test_result = grangercausalitytests(
                            df[[metric1, metric2]].dropna(),
                            maxlag=5,
                            verbose=False
                        )
                        p_values = [test_result[lag][0]['ssr_ftest'][1] for lag in range(1, 6)]
                        causality_results.append({
                            "from": metric1,
                            "to": metric2,
                            "p_values": p_values
                        })
                    except:
                        continue
        
        # Create causality heatmap
        causality_matrix = np.zeros((len(metrics), len(metrics)))
        for result in causality_results:
            i = metrics.index(result["from"])
            j = metrics.index(result["to"])
            causality_matrix[i, j] = np.mean(result["p_values"])
        
        fig.add_trace(
            go.Heatmap(
                z=causality_matrix,
                x=metrics,
                y=metrics,
                colorscale="RdYlBu_r",
                zmin=0,
                zmax=1,
                text=np.round(causality_matrix, 3),
                texttemplate="%{text}",
                textfont={"size": 10}
            ),
            row=1, col=1
        )
        
        # Power Analysis
        effect_sizes = np.linspace(0.1, 0.5, 10)
        sample_sizes = np.linspace(10, 100, 10)
        power_matrix = np.zeros((len(effect_sizes), len(sample_sizes)))
        
        for i, effect_size in enumerate(effect_sizes):
            for j, sample_size in enumerate(sample_sizes):
                power = tt_ind_solve_power(
                    effect_size=effect_size,
                    nobs1=sample_size,
                    alpha=0.05,
                    ratio=1.0
                )
                power_matrix[i, j] = power
        
        fig.add_trace(
            go.Heatmap(
                z=power_matrix,
                x=sample_sizes,
                y=effect_sizes,
                colorscale="Viridis",
                zmin=0,
                zmax=1,
                text=np.round(power_matrix, 2),
                texttemplate="%{text}",
                textfont={"size": 10}
            ),
            row=1, col=2
        )
        
        # Multiple Comparison Tests
        strategy_groups = df.groupby("strategy.current")
        p_values = []
        for strategy1, group1 in strategy_groups:
            for strategy2, group2 in strategy_groups:
                if strategy1 != strategy2:
                    _, p = mannwhitneyu(
                        group1["strategy.avg_selection_time"],
                        group2["strategy.avg_selection_time"]
                    )
                    p_values.append(p)
        
        # Apply Bonferroni correction
        reject, p_corrected, _, _ = multipletests(p_values, alpha=0.05, method='bonferroni')
        
        fig.add_trace(
            go.Bar(
                x=list(range(len(p_values))),
                y=p_corrected,
                name="Corrected p-values",
                marker_color=["red" if r else "blue" for r in reject]
            ),
            row=2, col=1
        )
        
        # Non-parametric Tests
        kruskal_results = []
        for metric in metrics:
            groups = [group[metric].values for _, group in strategy_groups]
            stat, p = kruskal(*groups)
            kruskal_results.append({
                "metric": metric,
                "statistic": stat,
                "p_value": p
            })
        
        kruskal_df = pd.DataFrame(kruskal_results)
        fig.add_trace(
            go.Bar(
                x=kruskal_df["metric"],
                y=kruskal_df["statistic"],
                name="Kruskal-Wallis Statistic",
                marker_color=["red" if p < 0.05 else "blue" for p in kruskal_df["p_value"]]
            ),
            row=2, col=2
        )
        
        # Time Series Stationarity
        stationarity_results = []
        for metric in metrics:
            # ADF Test
            adf_result = adfuller(df[metric].dropna())
            # KPSS Test
            kpss_result = kpss(df[metric].dropna())
            
            stationarity_results.append({
                "metric": metric,
                "adf_statistic": adf_result[0],
                "adf_p_value": adf_result[1],
                "kpss_statistic": kpss_result[0],
                "kpss_p_value": kpss_result[1]
            })
        
        stationarity_df = pd.DataFrame(stationarity_results)
        fig.add_trace(
            go.Table(
                header=dict(values=["Metric", "ADF Stat", "ADF p-value", "KPSS Stat", "KPSS p-value"]),
                cells=dict(values=[
                    stationarity_df["metric"],
                    np.round(stationarity_df["adf_statistic"], 3),
                    np.round(stationarity_df["adf_p_value"], 3),
                    np.round(stationarity_df["kpss_statistic"], 3),
                    np.round(stationarity_df["kpss_p_value"], 3)
                ])
            ),
            row=3, col=1
        )
        
        # Statistical Power
        power_results = []
        for metric in metrics:
            for strategy1, group1 in strategy_groups:
                for strategy2, group2 in strategy_groups:
                    if strategy1 != strategy2:
                        effect_size = (group1[metric].mean() - group2[metric].mean()) / np.sqrt(
                            (group1[metric].var() + group2[metric].var()) / 2
                        )
                        power = tt_ind_solve_power(
                            effect_size=abs(effect_size),
                            nobs1=len(group1),
                            alpha=0.05,
                            ratio=len(group2)/len(group1)
                        )
                        power_results.append({
                            "metric": metric,
                            "strategy1": strategy1,
                            "strategy2": strategy2,
                            "power": power
                        })
        
        power_df = pd.DataFrame(power_results)
        fig.add_trace(
            go.Heatmap(
                z=power_df.pivot(
                    index=["metric", "strategy1"],
                    columns="strategy2",
                    values="power"
                ).values,
                colorscale="Viridis",
                zmin=0,
                zmax=1
            ),
            row=3, col=2
        )
        
        fig.update_layout(
            height=1200,
            title_text="Advanced Statistical Analysis",
            showlegend=True
        )
        
        return fig
    
    def create_performance_degradation_analysis(self, metrics_history: List[Dict]) -> go.Figure:
        """Create a performance degradation analysis visualization.
        
        Args:
            metrics_history: List of metrics dictionaries
            
        Returns:
            Plotly figure containing the performance degradation analysis
        """
        df = pd.DataFrame(metrics_history)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Performance Degradation Over Time",
                "Degradation Rate Analysis",
                "Recovery Analysis",
                "Degradation Patterns"
            )
        )
        
        # Performance Degradation Over Time
        metrics = [
            "strategy.avg_selection_time",
            "strategy.success_rate",
            "strategy.load_balance_score"
        ]
        
        for metric in metrics:
            # Calculate moving average
            ma = df[metric].rolling(window=10).mean()
            # Calculate degradation
            degradation = (ma - ma.shift(1)) / ma.shift(1)
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=degradation * 100,
                    name=f"{metric} Degradation (%)",
                    line=dict(color=self.color_palette[df["strategy.current"].iloc[0]])
                ),
                row=1, col=1
            )
        
        # Degradation Rate Analysis
        degradation_rates = []
        for strategy, group in df.groupby("strategy.current"):
            for metric in metrics:
                ma = group[metric].rolling(window=10).mean()
                degradation = (ma - ma.shift(1)) / ma.shift(1)
                degradation_rates.append({
                    "strategy": strategy,
                    "metric": metric,
                    "rate": degradation.mean()
                })
        
        degradation_df = pd.DataFrame(degradation_rates)
        fig.add_trace(
            go.Bar(
                x=[f"{row['strategy']} - {row['metric']}" for _, row in degradation_df.iterrows()],
                y=degradation_df["rate"] * 100,
                name="Degradation Rate (%)",
                marker_color=[self.color_palette[s] for s in degradation_df["strategy"]]
            ),
            row=1, col=2
        )
        
        # Recovery Analysis
        recovery_times = []
        for strategy, group in df.groupby("strategy.current"):
            for metric in metrics:
                ma = group[metric].rolling(window=10).mean()
                degradation = (ma - ma.shift(1)) / ma.shift(1)
                recovery_points = degradation[degradation < 0].index
                if len(recovery_points) > 1:
                    recovery_time = np.mean(np.diff(recovery_points))
                    recovery_times.append({
                        "strategy": strategy,
                        "metric": metric,
                        "recovery_time": recovery_time
                    })
        
        recovery_df = pd.DataFrame(recovery_times)
        fig.add_trace(
            go.Bar(
                x=[f"{row['strategy']} - {row['metric']}" for _, row in recovery_df.iterrows()],
                y=recovery_df["recovery_time"],
                name="Recovery Time",
                marker_color=[self.color_palette[s] for s in recovery_df["strategy"]]
            ),
            row=2, col=1
        )
        
        # Degradation Patterns
        pattern_results = []
        for strategy, group in df.groupby("strategy.current"):
            for metric in metrics:
                ma = group[metric].rolling(window=10).mean()
                degradation = (ma - ma.shift(1)) / ma.shift(1)
                pattern_results.append({
                    "strategy": strategy,
                    "metric": metric,
                    "pattern": degradation.value_counts().head(3).to_dict()
                })
        
        pattern_df = pd.DataFrame(pattern_results)
        fig.add_trace(
            go.Heatmap(
                z=[[len(p) for p in pattern_df["pattern"]]],
                x=pattern_df["metric"],
                y=pattern_df["strategy"],
                colorscale="Viridis"
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Performance Degradation Analysis",
            showlegend=True
        )
        
        return fig
    
    def save_visualizations(self, metrics_history: List[Dict], output_dir: str):
        """Save all visualizations to HTML files.
        
        Args:
            metrics_history: List of metrics dictionaries
            output_dir: Directory to save visualizations
        """
        # Create existing visualizations
        dashboard = self.create_performance_dashboard(metrics_history)
        dashboard.write_html(f"{output_dir}/performance_dashboard.html")
        
        heatmap = self.create_node_health_heatmap(metrics_history)
        heatmap.write_html(f"{output_dir}/node_health_heatmap.html")
        
        comparison = self.create_strategy_comparison(metrics_history)
        comparison.write_html(f"{output_dir}/strategy_comparison.html")
        
        transition_analysis = self.create_transition_analysis(metrics_history)
        if transition_analysis:
            transition_analysis.write_html(f"{output_dir}/transition_analysis.html")
        
        # Create new visualizations
        correlation = self.create_correlation_analysis(metrics_history)
        correlation.write_html(f"{output_dir}/correlation_analysis.html")
        
        trend = self.create_trend_prediction(metrics_history, "strategy.avg_selection_time")
        trend.write_html(f"{output_dir}/trend_prediction.html")
        
        workload_patterns = self.create_workload_pattern_analysis(metrics_history)
        workload_patterns.write_html(f"{output_dir}/workload_patterns.html")
        
        strategy_matrix = self.create_strategy_effectiveness_matrix(metrics_history)
        strategy_matrix.write_html(f"{output_dir}/strategy_effectiveness.html")
        
        # Create statistical analysis visualizations
        statistical_analysis = self.create_statistical_analysis(metrics_history)
        statistical_analysis.write_html(f"{output_dir}/statistical_analysis.html")
        
        anomaly_detection = self.create_performance_anomaly_detection(metrics_history)
        anomaly_detection.write_html(f"{output_dir}/anomaly_detection.html")
        
        strategy_impact = self.create_strategy_impact_analysis(metrics_history)
        strategy_impact.write_html(f"{output_dir}/strategy_impact.html")
        
        # Create advanced statistical analysis visualizations
        advanced_stats = self.create_advanced_statistical_analysis(metrics_history)
        advanced_stats.write_html(f"{output_dir}/advanced_statistical_analysis.html")
        
        degradation = self.create_performance_degradation_analysis(metrics_history)
        degradation.write_html(f"{output_dir}/performance_degradation.html") 