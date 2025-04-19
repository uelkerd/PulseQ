"""
Report generator for PulseQ framework.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px
from jinja2 import Environment, FileSystemLoader


class ReportGenerator:
    """Generates detailed test reports in various formats."""

    def __init__(self, output_dir: str = "reports"):
        """Initialize the report generator.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_html_report(
        self,
        test_results: List[Dict],
        metrics: Dict,
        node_stats: Dict,
        output_file: Optional[str] = None,
    ) -> str:
        """Generate HTML report with interactive visualizations.

        Args:
            test_results: List of test results
            metrics: Performance metrics
            node_stats: Node statistics
            output_file: Optional output file path

        Returns:
            Path to generated report
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"report_{timestamp}.html")

        # Prepare data for visualizations
        df = pd.DataFrame(test_results)

        # Create visualizations
        test_status_fig = px.pie(
            df, values="count", names="status", title="Test Status Distribution"
        )

        duration_fig = px.box(df, y="duration", title="Test Duration Distribution")

        node_load_fig = px.bar(
            pd.DataFrame(node_stats),
            x="node_id",
            y="load",
            title="Node Load Distribution",
        )

        # Render template
        template = self.env.get_template("report.html")
        html_content = template.render(
            test_results=test_results,
            metrics=metrics,
            node_stats=node_stats,
            test_status_fig=test_status_fig.to_html(),
            duration_fig=duration_fig.to_html(),
            node_load_fig=node_load_fig.to_html(),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Save report
        with open(output_file, "w") as f:
            f.write(html_content)

        return output_file

    def generate_json_report(
        self,
        test_results: List[Dict],
        metrics: Dict,
        node_stats: Dict,
        output_file: Optional[str] = None,
    ) -> str:
        """Generate JSON report with detailed test data.

        Args:
            test_results: List of test results
            metrics: Performance metrics
            node_stats: Node statistics
            output_file: Optional output file path

        Returns:
            Path to generated report
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"report_{timestamp}.json")

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_results": test_results,
            "metrics": metrics,
            "node_stats": node_stats,
        }

        with open(output_file, "w") as f:
            json.dump(report_data, f, indent=2)

        return output_file

    def generate_csv_report(
        self, test_results: List[Dict], output_file: Optional[str] = None
    ) -> str:
        """Generate CSV report with test results.

        Args:
            test_results: List of test results
            output_file: Optional output file path

        Returns:
            Path to generated report
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"report_{timestamp}.csv")

        df = pd.DataFrame(test_results)
        df.to_csv(output_file, index=False)

        return output_file

    def generate_summary_report(
        self,
        test_results: List[Dict],
        metrics: Dict,
        node_stats: Dict,
        output_file: Optional[str] = None,
    ) -> str:
        """Generate a summary report with key metrics and statistics.

        Args:
            test_results: List of test results
            metrics: Performance metrics
            node_stats: Node statistics
            output_file: Optional output file path

        Returns:
            Path to generated report
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"summary_{timestamp}.txt")

        # Calculate summary statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r["status"] == "passed")
        failed_tests = sum(1 for r in test_results if r["status"] == "failed")
        error_tests = sum(1 for r in test_results if r["status"] == "error")

        avg_duration = sum(r["duration"] for r in test_results) / total_tests
        max_duration = max(r["duration"] for r in test_results)
        min_duration = min(r["duration"] for r in test_results)

        # Generate summary content
        summary = f"""PulseQ Test Summary Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Test Execution Summary:
---------------------
Total Tests: {total_tests}
Passed: {passed_tests} ({passed_tests/total_tests:.1%})
Failed: {failed_tests} ({failed_tests/total_tests:.1%})
Errors: {error_tests} ({error_tests/total_tests:.1%})

Duration Statistics:
------------------
Average Duration: {avg_duration:.2f}s
Minimum Duration: {min_duration:.2f}s
Maximum Duration: {max_duration:.2f}s

Performance Metrics:
------------------
Average Response Time: {metrics.get('avg_response_time', 0):.2f}ms
Throughput: {metrics.get('throughput', 0):.2f} req/s
Error Rate: {metrics.get('error_rate', 0):.2%}

Node Statistics:
--------------
Total Nodes: {len(node_stats)}
Average Load: {sum(s['load'] for s in node_stats)/len(node_stats):.1%}
Max Load: {max(s['load'] for s in node_stats):.1%}
Min Load: {min(s['load'] for s in node_stats):.1%}
"""

        with open(output_file, "w") as f:
            f.write(summary)

        return output_file
