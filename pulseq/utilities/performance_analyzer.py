import json
import os
import gc
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any

class PerformanceAnalyzer:
    def __init__(self, history_file: str = "test_results/metrics/performance_history.json"):
        """Initialize the Performance Analyzer.
        
        Args:
            history_file: Path to store historical performance data
        """
        self.history_file = history_file
        self.history_dir = os.path.dirname(history_file)
        os.makedirs(self.history_dir, exist_ok=True)
        self.current_metrics = {}
        self.load_history()

    def load_history(self) -> None:
        """Load historical performance data."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self) -> None:
        """Save performance history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def record_metrics(self, test_name: str, metrics: Dict[str, Any]) -> None:
        """Record metrics for a test run.
        
        Args:
            test_name: Name of the test
            metrics: Dictionary of performance metrics
        """
        timestamp = datetime.now().isoformat()
        self.current_metrics[test_name] = {
            'timestamp': timestamp,
            'metrics': metrics
        }

    def analyze_trends(self, test_name: str, metric_name: str) -> Dict[str, float]:
        """Analyze trends for a specific metric with enhanced statistics.
        
        Args:
            test_name: Name of the test
            metric_name: Name of the metric to analyze
            
        Returns:
            Dictionary containing trend analysis results
        """
        values = [run['metrics'][metric_name] 
                 for run in self.history 
                 if run['test_name'] == test_name]
        
        if not values:
            return {}

        # Calculate percentiles
        percentiles = np.percentile(values, [25, 50, 75, 90, 95, 99])
        
        # Calculate trend
        x = range(len(values))
        trend = np.polyfit(x, values, 1)
        trend_line = np.poly1d(trend)
        
        # Calculate rate of change
        rate_of_change = (values[-1] - values[0]) / len(values) if len(values) > 1 else 0
        
        return {
            'mean': np.mean(values),
            'std_dev': np.std(values),
            'min': min(values),
            'max': max(values),
            'median': percentiles[1],
            'p25': percentiles[0],
            'p75': percentiles[2],
            'p90': percentiles[3],
            'p95': percentiles[4],
            'p99': percentiles[5],
            'trend_slope': trend[0],
            'trend_intercept': trend[1],
            'rate_of_change': rate_of_change,
            'sample_size': len(values),
            'coefficient_of_variation': np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
        }

    def detect_regressions(self, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect performance regressions.
        
        Args:
            threshold: Number of standard deviations to consider as regression
            
        Returns:
            List of detected regressions
        """
        regressions = []
        
        for test_name, current in self.current_metrics.items():
            for metric_name, value in current['metrics'].items():
                trends = self.analyze_trends(test_name, metric_name)
                if not trends:
                    continue
                
                z_score = (value - trends['mean']) / trends['std_dev']
                if z_score > threshold:
                    regressions.append({
                        'test_name': test_name,
                        'metric_name': metric_name,
                        'current_value': value,
                        'historical_mean': trends['mean'],
                        'z_score': z_score
                    })
        
        return regressions

    def generate_trend_plots(self, output_dir: str = "test_results/trends") -> None:
        """Generate trend visualization plots.
        
        Args:
            output_dir: Directory to save trend plots
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for test_name in set(run['test_name'] for run in self.history):
            # Line chart for time series
            self._generate_time_series_plot(test_name, output_dir)
            
            # Box plot for distribution
            self._generate_box_plot(test_name, output_dir)
            
            # Heatmap for correlation
            self._generate_correlation_heatmap(test_name, output_dir)
            
            # Resource usage stacked area chart
            self._generate_resource_usage_plot(test_name, output_dir)

    def _generate_time_series_plot(self, test_name: str, output_dir: str) -> None:
        """Generate time series plot for a test."""
        plt.figure(figsize=(12, 6))
        
        metrics = set()
        for run in self.history:
            if run['test_name'] == test_name:
                metrics.update(run['metrics'].keys())
        
        for metric in metrics:
            values = [run['metrics'].get(metric) 
                     for run in self.history 
                     if run['test_name'] == test_name]
            timestamps = [run['timestamp'] 
                        for run in self.history 
                        if run['test_name'] == test_name]
            
            plt.plot(timestamps, values, label=metric, marker='o')
        
        plt.title(f"Performance Trends - {test_name}")
        plt.xlabel("Timestamp")
        plt.ylabel("Value")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        plt.savefig(os.path.join(output_dir, f"{test_name}_time_series.png"))
        plt.close()

    def _generate_box_plot(self, test_name: str, output_dir: str) -> None:
        """Generate box plot for metric distributions."""
        plt.figure(figsize=(10, 6))
        
        data = []
        labels = []
        
        metrics = set()
        for run in self.history:
            if run['test_name'] == test_name:
                metrics.update(run['metrics'].keys())
        
        for metric in metrics:
            values = [run['metrics'].get(metric) 
                     for run in self.history 
                     if run['test_name'] == test_name]
            data.append(values)
            labels.append(metric)
        
        plt.boxplot(data, labels=labels)
        plt.title(f"Metric Distributions - {test_name}")
        plt.ylabel("Value")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        
        plt.savefig(os.path.join(output_dir, f"{test_name}_distributions.png"))
        plt.close()

    def _generate_correlation_heatmap(self, test_name: str, output_dir: str) -> None:
        """Generate correlation heatmap between metrics."""
        metrics = set()
        for run in self.history:
            if run['test_name'] == test_name:
                metrics.update(run['metrics'].keys())
        
        # Create correlation matrix
        metric_data = {metric: [] for metric in metrics}
        for run in self.history:
            if run['test_name'] == test_name:
                for metric in metrics:
                    metric_data[metric].append(run['metrics'].get(metric, 0))
        
        correlation_matrix = np.corrcoef([metric_data[m] for m in metrics])
        
        # Plot heatmap
        plt.figure(figsize=(10, 8))
        plt.imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
        plt.colorbar()
        
        # Add labels
        plt.xticks(range(len(metrics)), list(metrics), rotation=45)
        plt.yticks(range(len(metrics)), list(metrics))
        
        # Add correlation values
        for i in range(len(metrics)):
            for j in range(len(metrics)):
                plt.text(j, i, f"{correlation_matrix[i, j]:.2f}",
                        ha="center", va="center")
        
        plt.title(f"Metric Correlations - {test_name}")
        plt.tight_layout()
        
        plt.savefig(os.path.join(output_dir, f"{test_name}_correlations.png"))
        plt.close()

    def _generate_resource_usage_plot(self, test_name: str, output_dir: str) -> None:
        """Generate stacked area chart for resource usage."""
        plt.figure(figsize=(12, 6))
        
        timestamps = [run['timestamp'] 
                     for run in self.history 
                     if run['test_name'] == test_name]
        
        resource_metrics = ['memory_usage', 'cpu_percent']
        data = {metric: [run['metrics'].get(metric, 0) 
                        for run in self.history 
                        if run['test_name'] == test_name]
                for metric in resource_metrics}
        
        plt.stackplot(timestamps, 
                     data.values(),
                     labels=data.keys(),
                     alpha=0.7)
        
        plt.title(f"Resource Usage Over Time - {test_name}")
        plt.xlabel("Timestamp")
        plt.ylabel("Usage (%)")
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        
        plt.savefig(os.path.join(output_dir, f"{test_name}_resource_usage.png"))
        plt.close()

    def cleanup_resources(self) -> None:
        """Clean up resources and trigger garbage collection."""
        gc.collect()
        
    def save_run_metrics(self) -> None:
        """Save current run metrics to history."""
        for test_name, data in self.current_metrics.items():
            self.history.append({
                'test_name': test_name,
                'timestamp': data['timestamp'],
                'metrics': data['metrics']
            })
        self.save_history()

    def generate_report(self, output_file: str = "test_results/performance_report.html") -> None:
        """Generate HTML performance report.
        
        Args:
            output_file: Path to save the HTML report
        """
        report_template = """
        <html>
        <head>
            <title>Performance Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .regression { color: red; }
                .improvement { color: green; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .trend-image { max-width: 800px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>Performance Test Report</h1>
            <h2>Test Run Summary</h2>
            {summary_table}
            
            <h2>Performance Regressions</h2>
            {regression_table}
            
            <h2>Trend Analysis</h2>
            {trend_analysis}
            
            <h2>Trend Visualizations</h2>
            {trend_images}
        </body>
        </html>
        """
        
        # Generate report sections
        summary_table = self._generate_summary_table()
        regression_table = self._generate_regression_table()
        trend_analysis = self._generate_trend_analysis()
        trend_images = self._generate_trend_images()
        
        # Combine into final report
        report_content = report_template.format(
            summary_table=summary_table,
            regression_table=regression_table,
            trend_analysis=trend_analysis,
            trend_images=trend_images
        )
        
        # Save report
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(report_content)

    def _generate_summary_table(self) -> str:
        """Generate HTML summary table."""
        rows = []
        for test_name, data in self.current_metrics.items():
            metrics_rows = []
            for metric_name, value in data['metrics'].items():
                metrics_rows.append(f"<tr><td>{metric_name}</td><td>{value}</td></tr>")
            
            rows.append(f"""
                <tr>
                    <td rowspan="{len(data['metrics'])}">{test_name}</td>
                    {metrics_rows[0]}
                </tr>
                {"".join(metrics_rows[1:])}
            """)
        
        return f"""
            <table>
                <tr>
                    <th>Test</th>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                {"".join(rows)}
            </table>
        """

    def _generate_regression_table(self) -> str:
        """Generate HTML regression table."""
        regressions = self.detect_regressions()
        if not regressions:
            return "<p>No performance regressions detected.</p>"
        
        rows = []
        for reg in regressions:
            rows.append(f"""
                <tr class="regression">
                    <td>{reg['test_name']}</td>
                    <td>{reg['metric_name']}</td>
                    <td>{reg['current_value']:.2f}</td>
                    <td>{reg['historical_mean']:.2f}</td>
                    <td>{reg['z_score']:.2f}</td>
                </tr>
            """)
        
        return f"""
            <table>
                <tr>
                    <th>Test</th>
                    <th>Metric</th>
                    <th>Current Value</th>
                    <th>Historical Mean</th>
                    <th>Z-Score</th>
                </tr>
                {"".join(rows)}
            </table>
        """

    def _generate_trend_analysis(self) -> str:
        """Generate HTML trend analysis section."""
        sections = []
        for test_name in self.current_metrics:
            metrics = self.current_metrics[test_name]['metrics']
            for metric_name in metrics:
                trends = self.analyze_trends(test_name, metric_name)
                if trends:
                    sections.append(f"""
                        <h3>{test_name} - {metric_name}</h3>
                        <ul>
                            <li>Mean: {trends['mean']:.2f}</li>
                            <li>Standard Deviation: {trends['std_dev']:.2f}</li>
                            <li>Min: {trends['min']:.2f}</li>
                            <li>Max: {trends['max']:.2f}</li>
                            <li>Trend: {"Improving" if trends['trend_slope'] < 0 else "Degrading"}</li>
                        </ul>
                    """)
        
        return "".join(sections)

    def _generate_trend_images(self) -> str:
        """Generate HTML trend images section."""
        images = []
        trend_dir = "test_results/trends"
        if os.path.exists(trend_dir):
            for test_name in self.current_metrics:
                image_path = f"{trend_dir}/{test_name}_time_series.png"
                if os.path.exists(image_path):
                    images.append(f"""
                        <div>
                            <h3>{test_name}</h3>
                            <img src="{image_path}" class="trend-image" />
                        </div>
                    """)
        
        return "".join(images) 