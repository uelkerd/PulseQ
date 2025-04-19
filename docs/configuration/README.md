# PulseQ Configuration Guide

## Overview

This guide covers all configuration options available in the PulseQ framework, from basic setup to advanced customization.

## Table of Contents

1. [Basic Configuration](#basic-configuration)
2. [Node Configuration](#node-configuration)
3. [Test Configuration](#test-configuration)
4. [Framework Configuration](#framework-configuration)
5. [Environment Configuration](#environment-configuration)
6. [Advanced Configuration](#advanced-configuration)

## Basic Configuration

### Framework Setup

Create a `pulseq_config.yaml` file in your project root:

```yaml
framework:
  name: "PulseQ"
  version: "1.0.0"
  environment: "development"
  log_level: "INFO"
  max_workers: 4
```

### Logging Configuration

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "pulseq.log"
  max_size: 10485760 # 10MB
  backup_count: 5
```

## Node Configuration

### Basic Node Setup

```yaml
nodes:
  - id: "node1"
    host: "localhost"
    port: 8000
    capabilities:
      os: "linux"
      browser: "chrome"
      memory: "8GB"
    max_concurrent_tests: 5
```

### Node Health Monitoring

```yaml
node_health:
  heartbeat_interval: 30 # seconds
  timeout: 60 # seconds
  retry_attempts: 3
  retry_delay: 5 # seconds
```

## Test Configuration

### Test Definition

```yaml
tests:
  - id: "test1"
    name: "api_test"
    type: "api"
    priority: "high"
    timeout: 30 # seconds
    max_retries: 3
    requirements:
      os: "linux"
      browser: "chrome"
    metrics:
      - "response_time"
      - "memory_usage"
      - "cpu_usage"
```

### Test Categories

```yaml
test_categories:
  api:
    timeout: 30
    retry_attempts: 3
    metrics:
      - "response_time"
      - "status_code"
  ui:
    timeout: 60
    retry_attempts: 2
    metrics:
      - "load_time"
      - "render_time"
  performance:
    timeout: 300
    retry_attempts: 1
    metrics:
      - "throughput"
      - "latency"
```

## Framework Configuration

### Test Distribution

```yaml
distribution:
  strategy: "round_robin" # or "least_load" or "capability_match"
  load_balancing:
    enabled: true
    interval: 5 # seconds
    threshold: 0.8 # max load percentage
  priority:
    enabled: true
    levels:
      - "critical"
      - "high"
      - "medium"
      - "low"
```

### Result Aggregation

```yaml
results:
  aggregation:
    enabled: true
    interval: 5 # seconds
    persist: true
  storage:
    type: "file" # or "database"
    path: "results/"
    format: "json" # or "csv"
  retention:
    days: 30
    max_size: 1073741824 # 1GB
```

## Environment Configuration

### Development Environment

```yaml
environment: "development"
development:
  debug: true
  log_level: "DEBUG"
  test_timeout: 60
  max_workers: 2
```

### Production Environment

```yaml
environment: "production"
production:
  debug: false
  log_level: "INFO"
  test_timeout: 300
  max_workers: 8
  security:
    ssl: true
    auth: true
```

## Advanced Configuration

### Custom Load Balancing

```yaml
load_balancing:
  strategy: "custom"
  custom_strategy:
    name: "weighted_round_robin"
    weights:
      node1: 3
      node2: 2
      node3: 1
    factors:
      - "cpu_usage"
      - "memory_usage"
      - "network_latency"
```

### Metrics Collection

```yaml
metrics:
  collection:
    enabled: true
    interval: 1 # seconds
    retention: 3600 # seconds
  types:
    system:
      - "cpu_usage"
      - "memory_usage"
      - "disk_usage"
    network:
      - "latency"
      - "bandwidth"
      - "packet_loss"
    application:
      - "response_time"
      - "throughput"
      - "error_rate"
```

### Alerting Configuration

```yaml
alerts:
  enabled: true
  channels:
    - type: "email"
      recipients:
        - "team@example.com"
      conditions:
        - metric: "error_rate"
          threshold: 0.1
          duration: 300
    - type: "slack"
      webhook: "https://hooks.slack.com/services/..."
      conditions:
        - metric: "response_time"
          threshold: 1000
          duration: 60
```

## Configuration Best Practices

1. **Environment-Specific Configs**

   - Use separate config files for different environments
   - Use environment variables for sensitive data
   - Validate configurations on startup

2. **Node Management**

   - Define clear node capabilities
   - Set appropriate timeouts and retry limits
   - Monitor node health metrics

3. **Test Configuration**

   - Use meaningful test IDs and names
   - Set appropriate timeouts and retry counts
   - Define required metrics for analysis

4. **Result Management**
   - Configure appropriate retention periods
   - Choose suitable storage formats
   - Set up proper backup strategies

## Configuration Validation

The framework validates configurations on startup. Common validation checks include:

```python
from pulseq.config import validate_config

# Validate configuration
try:
    validate_config(config)
except ValidationError as e:
    print(f"Configuration error: {e}")
```

## Dynamic Configuration

Configurations can be updated at runtime:

```python
from pulseq.config import update_config

# Update configuration
new_config = {
    "framework": {
        "max_workers": 8
    }
}
update_config(new_config)
```

## Troubleshooting Configuration Issues

1. **Common Issues**

   - Invalid YAML syntax
   - Missing required fields
   - Invalid value types
   - Conflicting settings

2. **Debugging Tips**

   - Enable debug logging
   - Check configuration files
   - Validate environment variables
   - Monitor configuration changes

3. **Configuration Recovery**
   - Keep backup configurations
   - Use version control
   - Implement rollback mechanisms
