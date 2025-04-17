# framework/conftest.py
import pytest

from framework.utilities.mock_server import MockServer


@pytest.fixture(scope="session")
def mock_server():
    """Start a mock server for testing and return the base URL."""
    server = MockServer(port=8000)
    base_url = server.start()
    yield base_url
    server.stop()


@pytest.fixture(scope="function")
def config(mock_server):
    """Override the config to use the mock server URL."""
    from framework.config import load_config

    config = load_config()
    config["base_url"] = mock_server
    return config
