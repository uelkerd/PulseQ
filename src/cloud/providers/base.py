from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class CloudProvider(ABC):
    """Base class for cloud provider implementations."""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the cloud provider with configuration."""
        pass

    @abstractmethod
    def create_test_environment(
        self, name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a test environment in the cloud."""
        pass

    @abstractmethod
    def destroy_test_environment(self, environment_id: str) -> None:
        """Destroy a test environment."""
        pass

    @abstractmethod
    def scale_environment(
        self, environment_id: str, scale_config: Dict[str, Any]
    ) -> None:
        """Scale the test environment resources."""
        pass

    @abstractmethod
    def get_environment_status(self, environment_id: str) -> Dict[str, Any]:
        """Get the status of a test environment."""
        pass

    @abstractmethod
    def list_environments(self) -> List[Dict[str, Any]]:
        """List all test environments."""
        pass

    @abstractmethod
    def get_cost_estimate(self, environment_id: Optional[str] = None) -> Dict[str, Any]:
        """Get cost estimate for environment(s)."""
        pass
