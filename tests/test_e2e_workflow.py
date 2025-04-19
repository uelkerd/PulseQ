def teardown_module(module):
    """Clean up after all tests in this module."""
    metrics.save_metrics()
