import pytest
import json
from pathlib import Path
from pulseq.config.config_manager import ConfigManager, LoadBalancerConfig, WorkloadPatternConfig, EdgeCaseConfig

@pytest.fixture
def config_file(tmp_path):
    """Create a temporary configuration file."""
    config = {
        "load_balancer": {
            "strategy": "least_connections",
            "health_check_interval": 5,
            "timeout": 30,
            "max_retries": 3
        },
        "workload_patterns": {
            "basic": {
                "requests_per_second": 100,
                "request_size": 1024,
                "duration": 60
            },
            "ecommerce": {
                "requests_per_second": 500,
                "request_size": 1024,
                "duration": 60,
                "peak_hours": [10, 14, 20]
            }
        },
        "edge_cases": {
            "cpu_saturation": {
                "cpu_usage": 0.95,
                "duration": 30
            }
        },
        "metrics": {
            "collection_interval": 1,
            "thresholds": {
                "success_rate": 0.8,
                "load_balance": 0.8,
                "response_time": 1000,
                "error_rate": 0.05
            }
        },
        "reporting": {
            "output_dir": "reports",
            "format": "html",
            "include_metrics": ["success_rate", "load_balance"]
        }
    }
    
    config_path = tmp_path / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)
    return config_path

def test_load_config(config_file):
    """Test loading and parsing of configuration file."""
    manager = ConfigManager(str(config_file))
    manager.load_config()
    
    assert isinstance(manager.load_balancer_config, LoadBalancerConfig)
    assert manager.load_balancer_config.strategy == "least_connections"
    assert manager.load_balancer_config.health_check_interval == 5
    
    assert "basic" in manager.workload_patterns
    assert "ecommerce" in manager.workload_patterns
    assert isinstance(manager.workload_patterns["basic"], WorkloadPatternConfig)
    
    assert "cpu_saturation" in manager.edge_cases
    assert isinstance(manager.edge_cases["cpu_saturation"], EdgeCaseConfig)
    
    assert manager.metrics_config.collection_interval == 1
    assert manager.metrics_config.thresholds["success_rate"] == 0.8
    
    assert manager.reporting_config.output_dir == "reports"
    assert manager.reporting_config.format == "html"

def test_get_workload_pattern(config_file):
    """Test retrieving specific workload patterns."""
    manager = ConfigManager(str(config_file))
    manager.load_config()
    
    pattern = manager.get_workload_pattern("basic")
    assert pattern.requests_per_second == 100
    assert pattern.request_size == 1024
    assert pattern.duration == 60
    
    pattern = manager.get_workload_pattern("ecommerce")
    assert pattern.requests_per_second == 500
    assert pattern.peak_hours == [10, 14, 20]
    
    with pytest.raises(KeyError):
        manager.get_workload_pattern("nonexistent")

def test_get_edge_case(config_file):
    """Test retrieving specific edge cases."""
    manager = ConfigManager(str(config_file))
    manager.load_config()
    
    case = manager.get_edge_case("cpu_saturation")
    assert case.cpu_usage == 0.95
    assert case.duration == 30
    
    with pytest.raises(KeyError):
        manager.get_edge_case("nonexistent")

def test_validate_workload_pattern(config_file):
    """Test workload pattern validation."""
    manager = ConfigManager(str(config_file))
    manager.load_config()
    
    pattern = WorkloadPatternConfig(
        requests_per_second=100,
        request_size=1024,
        duration=60
    )
    assert manager.validate_workload_pattern(pattern)
    
    pattern.requests_per_second = -1
    assert not manager.validate_workload_pattern(pattern)
    
    pattern.requests_per_second = 100
    pattern.peak_hours = [25]  # Invalid hour
    assert not manager.validate_workload_pattern(pattern)

def test_validate_edge_case(config_file):
    """Test edge case validation."""
    manager = ConfigManager(str(config_file))
    manager.load_config()
    
    case = EdgeCaseConfig(
        cpu_usage=0.5,
        duration=30
    )
    assert manager.validate_edge_case(case)
    
    case.cpu_usage = 1.5  # Invalid usage
    assert not manager.validate_edge_case(case)
    
    case.cpu_usage = 0.5
    case.duration = -1  # Invalid duration
    assert not manager.validate_edge_case(case)

def test_invalid_config(tmp_path):
    """Test handling of invalid configuration."""
    invalid_config = {
        "load_balancer": {
            "strategy": "invalid_strategy",  # Invalid strategy
            "health_check_interval": 0,      # Invalid interval
            "timeout": 30,
            "max_retries": 3
        }
    }
    
    config_path = tmp_path / "invalid_config.json"
    with open(config_path, 'w') as f:
        json.dump(invalid_config, f)
    
    manager = ConfigManager(str(config_path))
    with pytest.raises(Exception):
        manager.load_config() 