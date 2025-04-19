# PulseQ Quick Start Guide

## Installation

1. Install PulseQ using pip:

```bash
pip install pulseq
```

2. Verify installation:

```bash
pulseq --version
```

## Basic Usage

### 1. Initialize Project

Create a new PulseQ project:

```bash
pulseq init my-project
cd my-project
```

### 2. Configure Nodes

Edit `pulseq_config.yaml`:

```yaml
nodes:
  - id: "local"
    host: "localhost"
    port: 8000
    capabilities:
      os: "linux"
      browser: "chrome"
```

### 3. Create Your First Test

Create `tests/test_api.py`:

```python
from pulseq import TestCase

class APITest(TestCase):
    def test_get_users(self):
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)
```

### 4. Run Tests

Run all tests:

```bash
pulseq run
```

Run specific test:

```bash
pulseq run tests/test_api.py
```

## Advanced Usage

### Distributed Testing

1. Configure multiple nodes:

```yaml
nodes:
  - id: "node1"
    host: "node1.example.com"
    port: 8000
  - id: "node2"
    host: "node2.example.com"
    port: 8000
```

2. Run distributed tests:

```bash
pulseq run --distributed
```

### Test Categories

Organize tests by category:

```python
from pulseq import TestCase, category

@category("api")
class APITest(TestCase):
    pass

@category("performance")
class PerformanceTest(TestCase):
    pass
```

Run by category:

```bash
pulseq run --category api
```

### Metrics Collection

Enable metrics in test:

```python
class APITest(TestCase):
    def test_performance(self):
        with self.metrics() as m:
            response = self.client.get("/api/users")
            m.record("response_time", response.elapsed.total_seconds())
```

View metrics:

```bash
pulseq metrics
```

## Common Tasks

### 1. Create Test Suite

```python
from pulseq import TestSuite

suite = TestSuite("API Tests")
suite.add_test(APITest("test_get_users"))
suite.add_test(APITest("test_create_user"))
```

### 2. Configure Retries

```python
class APITest(TestCase):
    max_retries = 3
    retry_delay = 5  # seconds
```

### 3. Set Timeouts

```python
class APITest(TestCase):
    timeout = 30  # seconds
```

### 4. Use Test Data

```python
class APITest(TestCase):
    def test_create_user(self):
        user_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        response = self.client.post("/api/users", json=user_data)
        self.assertEqual(response.status_code, 201)
```

## Best Practices

1. **Test Organization**

   - Group related tests in classes
   - Use descriptive test names
   - Follow naming conventions

2. **Error Handling**

   - Use appropriate assertions
   - Handle expected exceptions
   - Clean up resources

3. **Performance**

   - Set appropriate timeouts
   - Use retries for flaky tests
   - Monitor resource usage

4. **Maintenance**
   - Keep tests independent
   - Use test fixtures
   - Document test requirements

## Troubleshooting

### Common Issues

1. **Node Connection**

```bash
# Check node status
pulseq nodes status

# Test node connection
pulseq nodes ping node1
```

2. **Test Failures**

```bash
# View test logs
pulseq logs

# Get detailed failure info
pulseq run --verbose
```

3. **Performance Issues**

```bash
# Monitor system metrics
pulseq metrics system

# Check test duration
pulseq metrics duration
```

### Debugging Tips

1. Enable debug logging:

```bash
pulseq run --log-level DEBUG
```

2. Run single test:

```bash
pulseq run tests/test_api.py::APITest::test_get_users
```

3. View test coverage:

```bash
pulseq coverage
```

## Next Steps

1. **Explore Documentation**

   - [API Reference](api/distributed_testing.md)
   - [Configuration Guide](configuration/README.md)
   - [Best Practices](best_practices.md)

2. **Advanced Features**

   - Custom test runners
   - Plugin development
   - CI/CD integration

3. **Community**
   - Join discussion forum
   - Contribute to development
   - Report issues
