from typing import Dict, Any, Type
from .providers.base import CloudProvider
from .providers.aws import AWSProvider
from .providers.gcp import GCPProvider
from .providers.azure import AzureProvider
import logging

logger = logging.getLogger(__name__)

class CloudManager:
    """Manages cloud providers and their operations."""
    
    _providers: Dict[str, Type[CloudProvider]] = {
        'aws': AWSProvider,
        'gcp': GCPProvider,
        'azure': AzureProvider
    }
    
    def __init__(self):
        self._active_provider = None
        self._provider_instance = None
    
    def initialize_provider(self, provider_name: str, config: Dict[str, Any]) -> None:
        """Initialize a cloud provider."""
        if provider_name not in self._providers:
            raise ValueError(f"Unsupported cloud provider: {provider_name}")
        
        try:
            provider_class = self._providers[provider_name]
            self._provider_instance = provider_class()
            self._provider_instance.initialize(config)
            self._active_provider = provider_name
            logger.info(f"Initialized {provider_name} cloud provider")
        except Exception as e:
            logger.error(f"Failed to initialize {provider_name} provider: {str(e)}")
            raise
    
    def create_test_environment(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a test environment using the active provider."""
        if not self._provider_instance:
            raise RuntimeError("No cloud provider initialized")
        
        try:
            return self._provider_instance.create_test_environment(name, config)
        except Exception as e:
            logger.error(f"Failed to create test environment: {str(e)}")
            raise
    
    def destroy_test_environment(self, environment_id: str) -> None:
        """Destroy a test environment using the active provider."""
        if not self._provider_instance:
            raise RuntimeError("No cloud provider initialized")
        
        try:
            self._provider_instance.destroy_test_environment(environment_id)
        except Exception as e:
            logger.error(f"Failed to destroy test environment: {str(e)}")
            raise
    
    def scale_environment(self, environment_id: str, scale_config: Dict[str, Any]) -> None:
        """Scale a test environment using the active provider."""
        if not self._provider_instance:
            raise RuntimeError("No cloud provider initialized")
        
        try:
            self._provider_instance.scale_environment(environment_id, scale_config)
        except Exception as e:
            logger.error(f"Failed to scale environment: {str(e)}")
            raise
    
    def get_environment_status(self, environment_id: str) -> Dict[str, Any]:
        """Get the status of a test environment."""
        if not self._provider_instance:
            raise RuntimeError("No cloud provider initialized")
        
        try:
            return self._provider_instance.get_environment_status(environment_id)
        except Exception as e:
            logger.error(f"Failed to get environment status: {str(e)}")
            raise
    
    def list_environments(self) -> list:
        """List all test environments."""
        if not self._provider_instance:
            raise RuntimeError("No cloud provider initialized")
        
        try:
            return self._provider_instance.list_environments()
        except Exception as e:
            logger.error(f"Failed to list environments: {str(e)}")
            raise
    
    def get_cost_estimate(self, environment_id: str = None) -> Dict[str, Any]:
        """Get cost estimate for environment(s)."""
        if not self._provider_instance:
            raise RuntimeError("No cloud provider initialized")
        
        try:
            return self._provider_instance.get_cost_estimate(environment_id)
        except Exception as e:
            logger.error(f"Failed to get cost estimate: {str(e)}")
            raise
    
    @property
    def active_provider(self) -> str:
        """Get the name of the active provider."""
        return self._active_provider
    
    @property
    def available_providers(self) -> list:
        """Get list of available cloud providers."""
        return list(self._providers.keys()) 