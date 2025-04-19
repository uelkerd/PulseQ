"""
Example usage patterns for the monitoring dashboard.
"""
from typing import Dict, Any
import asyncio
from datetime import datetime
from pulseq.monitoring.dashboard import MonitoringDashboard

async def run_basic_monitoring_example() -> Dict[str, Any]:
    """Example usage for basic monitoring dashboard."""
    dashboard = MonitoringDashboard()
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Get initial dashboard data
    initial_data = await dashboard.get_dashboard_data()
    
    # Wait for some updates
    await asyncio.sleep(120)  # 2 minutes
    
    # Get updated dashboard data
    updated_data = await dashboard.get_dashboard_data()
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "initial_data": initial_data,
        "updated_data": updated_data
    }

async def run_enterprise_monitoring_example() -> Dict[str, Any]:
    """Example usage for enterprise monitoring dashboard."""
    dashboard = MonitoringDashboard()
    
    # Set faster update interval
    await dashboard.set_update_interval(30)  # 30 seconds
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Monitor for 5 minutes
    data_points = []
    for _ in range(10):  # 10 updates over 5 minutes
        data = await dashboard.get_dashboard_data()
        data_points.append(data)
        await asyncio.sleep(30)
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "data_points": data_points,
        "monitoring_duration": "5 minutes",
        "update_interval": "30 seconds"
    }

async def run_compliance_monitoring_example() -> Dict[str, Any]:
    """Example usage for compliance monitoring dashboard."""
    dashboard = MonitoringDashboard()
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Focus on compliance metrics
    compliance_data = []
    for _ in range(5):  # 5 updates
        data = await dashboard.get_dashboard_data()
        compliance_data.append({
            "timestamp": data["last_updated"],
            "compliance_status": data["compliance_status"],
            "risk_scores": data["risk_scores"]
        })
        await asyncio.sleep(60)
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "compliance_data": compliance_data,
        "monitoring_duration": "5 minutes",
        "update_interval": "60 seconds"
    }

async def run_security_monitoring_example() -> Dict[str, Any]:
    """Example usage for security monitoring dashboard."""
    dashboard = MonitoringDashboard()
    
    # Set faster update interval for security monitoring
    await dashboard.set_update_interval(15)  # 15 seconds
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Focus on security metrics
    security_data = []
    for _ in range(20):  # 20 updates over 5 minutes
        data = await dashboard.get_dashboard_data()
        security_data.append({
            "timestamp": data["last_updated"],
            "security_alerts": data["security_alerts"],
            "risk_scores": data["risk_scores"]
        })
        await asyncio.sleep(15)
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "security_data": security_data,
        "monitoring_duration": "5 minutes",
        "update_interval": "15 seconds"
    }

async def run_performance_monitoring_example() -> Dict[str, Any]:
    """Example usage for performance monitoring dashboard."""
    dashboard = MonitoringDashboard()
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Focus on performance metrics
    performance_data = []
    for _ in range(6):  # 6 updates over 6 minutes
        data = await dashboard.get_dashboard_data()
        performance_data.append({
            "timestamp": data["last_updated"],
            "performance_metrics": data["performance_metrics"],
            "resource_utilization": data["resource_utilization"]
        })
        await asyncio.sleep(60)
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "performance_data": performance_data,
        "monitoring_duration": "6 minutes",
        "update_interval": "60 seconds"
    }

async def run_healthcare_monitoring_example() -> Dict[str, Any]:
    """Example usage for healthcare industry monitoring."""
    dashboard = MonitoringDashboard()
    
    # Set update interval for healthcare monitoring
    await dashboard.set_update_interval(30)  # 30 seconds
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Focus on healthcare-specific metrics
    healthcare_data = []
    for _ in range(10):  # 10 updates over 5 minutes
        data = await dashboard.get_dashboard_data()
        healthcare_data.append({
            "timestamp": data["last_updated"],
            "hipaa_compliance": data["compliance_status"]["hipaa_compliance"],
            "patient_data_security": data["security_alerts"]["active_threats"],
            "system_performance": data["performance_metrics"]["api_response_time"]
        })
        await asyncio.sleep(30)
    
    # Generate visualizations
    visualizations = await dashboard.generate_visualizations()
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "healthcare_data": healthcare_data,
        "visualizations": visualizations,
        "monitoring_duration": "5 minutes",
        "update_interval": "30 seconds"
    }

async def run_financial_monitoring_example() -> Dict[str, Any]:
    """Example usage for financial industry monitoring."""
    dashboard = MonitoringDashboard()
    
    # Set update interval for financial monitoring
    await dashboard.set_update_interval(15)  # 15 seconds
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Focus on financial-specific metrics
    financial_data = []
    for _ in range(20):  # 20 updates over 5 minutes
        data = await dashboard.get_dashboard_data()
        financial_data.append({
            "timestamp": data["last_updated"],
            "pci_dss_compliance": data["compliance_status"]["pci_dss_compliance"],
            "transaction_security": data["security_alerts"]["active_threats"],
            "system_performance": data["performance_metrics"]["api_response_time"]
        })
        await asyncio.sleep(15)
    
    # Generate visualizations
    visualizations = await dashboard.generate_visualizations()
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "financial_data": financial_data,
        "visualizations": visualizations,
        "monitoring_duration": "5 minutes",
        "update_interval": "15 seconds"
    }

async def run_government_monitoring_example() -> Dict[str, Any]:
    """Example usage for government sector monitoring."""
    dashboard = MonitoringDashboard()
    
    # Set update interval for government monitoring
    await dashboard.set_update_interval(60)  # 60 seconds
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Focus on government-specific metrics
    government_data = []
    for _ in range(5):  # 5 updates over 5 minutes
        data = await dashboard.get_dashboard_data()
        government_data.append({
            "timestamp": data["last_updated"],
            "fisma_compliance": data["compliance_status"]["fisma_compliance"],
            "security_clearance": data["security_alerts"]["active_threats"],
            "system_performance": data["performance_metrics"]["api_response_time"]
        })
        await asyncio.sleep(60)
    
    # Generate visualizations
    visualizations = await dashboard.generate_visualizations()
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "government_data": government_data,
        "visualizations": visualizations,
        "monitoring_duration": "5 minutes",
        "update_interval": "60 seconds"
    }

async def run_github_actions_integration() -> Dict[str, Any]:
    """Example usage for GitHub Actions CI/CD integration."""
    dashboard = MonitoringDashboard()
    
    # Set update interval for CI/CD monitoring
    await dashboard.set_update_interval(60)  # 60 seconds
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Focus on CI/CD metrics
    ci_cd_data = []
    for _ in range(5):  # 5 updates over 5 minutes
        data = await dashboard.get_dashboard_data()
        ci_cd_data.append({
            "timestamp": data["last_updated"],
            "build_success_rate": data["ci_cd_metrics"]["build_success_rate"],
            "test_coverage": data["ci_cd_metrics"]["test_coverage"],
            "deployment_frequency": data["ci_cd_metrics"]["deployment_frequency"],
            "lead_time": data["ci_cd_metrics"]["lead_time"],
            "mean_time_to_recovery": data["ci_cd_metrics"]["mean_time_to_recovery"]
        })
        await asyncio.sleep(60)
    
    # Generate visualizations
    visualizations = await dashboard.generate_visualizations()
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "ci_cd_data": ci_cd_data,
        "visualizations": visualizations,
        "monitoring_duration": "5 minutes",
        "update_interval": "60 seconds"
    }

async def run_gitlab_ci_integration() -> Dict[str, Any]:
    """Example usage for GitLab CI/CD integration."""
    dashboard = MonitoringDashboard()
    
    # Set update interval for CI/CD monitoring
    await dashboard.set_update_interval(60)  # 60 seconds
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Focus on CI/CD metrics
    ci_cd_data = []
    for _ in range(5):  # 5 updates over 5 minutes
        data = await dashboard.get_dashboard_data()
        ci_cd_data.append({
            "timestamp": data["last_updated"],
            "pipeline_success_rate": data["ci_cd_metrics"]["build_success_rate"],
            "test_coverage": data["ci_cd_metrics"]["test_coverage"],
            "deployment_frequency": data["ci_cd_metrics"]["deployment_frequency"],
            "lead_time": data["ci_cd_metrics"]["lead_time"],
            "mean_time_to_recovery": data["ci_cd_metrics"]["mean_time_to_recovery"]
        })
        await asyncio.sleep(60)
    
    # Generate visualizations
    visualizations = await dashboard.generate_visualizations()
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "ci_cd_data": ci_cd_data,
        "visualizations": visualizations,
        "monitoring_duration": "5 minutes",
        "update_interval": "60 seconds"
    }

async def run_jenkins_integration() -> Dict[str, Any]:
    """Example usage for Jenkins CI/CD integration."""
    dashboard = MonitoringDashboard()
    
    # Set update interval for CI/CD monitoring
    await dashboard.set_update_interval(60)  # 60 seconds
    
    # Start monitoring
    await dashboard.start_monitoring()
    
    # Focus on CI/CD metrics
    ci_cd_data = []
    for _ in range(5):  # 5 updates over 5 minutes
        data = await dashboard.get_dashboard_data()
        ci_cd_data.append({
            "timestamp": data["last_updated"],
            "build_success_rate": data["ci_cd_metrics"]["build_success_rate"],
            "test_coverage": data["ci_cd_metrics"]["test_coverage"],
            "deployment_frequency": data["ci_cd_metrics"]["deployment_frequency"],
            "lead_time": data["ci_cd_metrics"]["lead_time"],
            "mean_time_to_recovery": data["ci_cd_metrics"]["mean_time_to_recovery"]
        })
        await asyncio.sleep(60)
    
    # Generate visualizations
    visualizations = await dashboard.generate_visualizations()
    
    # Stop monitoring
    await dashboard.stop_monitoring()
    
    return {
        "ci_cd_data": ci_cd_data,
        "visualizations": visualizations,
        "monitoring_duration": "5 minutes",
        "update_interval": "60 seconds"
    }

async def main():
    """Run all monitoring examples."""
    examples = {
        "basic_monitoring": await run_basic_monitoring_example(),
        "enterprise_monitoring": await run_enterprise_monitoring_example(),
        "compliance_monitoring": await run_compliance_monitoring_example(),
        "security_monitoring": await run_security_monitoring_example(),
        "performance_monitoring": await run_performance_monitoring_example(),
        "healthcare_monitoring": await run_healthcare_monitoring_example(),
        "financial_monitoring": await run_financial_monitoring_example(),
        "government_monitoring": await run_government_monitoring_example(),
        "github_actions_integration": await run_github_actions_integration(),
        "gitlab_ci_integration": await run_gitlab_ci_integration(),
        "jenkins_integration": await run_jenkins_integration()
    }
    
    return examples

if __name__ == "__main__":
    results = asyncio.run(main())
    print("Monitoring examples completed successfully.") 