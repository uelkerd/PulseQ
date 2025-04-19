import pytest
from src.core.test_runner import TestRunner
from src.core.distributed_testing import DistributedTestManager
from src.core.caching import CacheManager
from src.core.monitoring import PerformanceMonitor

@pytest.fixture
def test_runner():
    return TestRunner()

@pytest.fixture
def distributed_manager():
    return DistributedTestManager()

@pytest.fixture
def cache_manager():
    return CacheManager()

@pytest.fixture
def performance_monitor():
    return PerformanceMonitor()

def test_test_execution_speed(benchmark, test_runner):
    """Benchmark test execution speed"""
    result = benchmark(test_runner.execute_test, "sample_test")
    assert result is not None

def test_distributed_test_speed(benchmark, distributed_manager):
    """Benchmark distributed test execution speed"""
    if not feature_flags.is_enabled('distributed_testing'):
        pytest.skip("Distributed testing feature not enabled")
    
    result = benchmark(distributed_manager.execute_distributed_test, 
                      "distributed_test",
                      nodes=5)
    assert result is not None

def test_cache_performance(benchmark, cache_manager):
    """Benchmark cache operations"""
    if not feature_flags.is_enabled('advanced_caching'):
        pytest.skip("Advanced caching feature not enabled")
    
    data = {"key": "value"}
    result = benchmark(cache_manager.set, "test_key", data)
    assert result is not None

def test_monitoring_overhead(benchmark, performance_monitor):
    """Benchmark monitoring overhead"""
    if not feature_flags.is_enabled('enhanced_monitoring'):
        pytest.skip("Enhanced monitoring feature not enabled")
    
    result = benchmark(performance_monitor.track_metric, 
                      "test_metric",
                      value=100)
    assert result is not None

def test_multi_env_switch_speed(benchmark):
    """Benchmark environment switching speed"""
    if not feature_flags.is_enabled('multi_env_testing'):
        pytest.skip("Multi-environment testing feature not enabled")
    
    result = benchmark(lambda: os.environ.get('TEST_ENVIRONMENT'))
    assert result is not None 