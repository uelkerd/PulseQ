import logging
from typing import Any, Dict, List, Optional

from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.resource import ResourceManagementClient

from .base import CloudProvider

logger = logging.getLogger(__name__)


class AzureProvider(CloudProvider):
    """Azure cloud provider implementation."""

    def __init__(self):
        self.container_client = None
        self.resource_client = None
        self.config = None

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Azure provider with configuration."""
        self.config = config
        try:
            # Initialize Azure clients
            credential = DefaultAzureCredential()
            self.container_client = ContainerServiceClient(
                credential=credential, subscription_id=config.get("subscription_id")
            )
            self.resource_client = ResourceManagementClient(
                credential=credential, subscription_id=config.get("subscription_id")
            )

            # Set resource group and location
            self.resource_group = config.get("resource_group")
            self.location = config.get("location", "eastus")

        except Exception as e:
            logger.error(f"Failed to initialize Azure provider: {str(e)}")
            raise

    def create_test_environment(
        self, name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a test environment in Azure."""
        try:
            # Create AKS cluster
            cluster = {
                "location": self.location,
                "dns_prefix": f"pulseq-{name}",
                "agent_pool_profiles": [
                    {
                        "name": "default",
                        "count": config.get("node_count", 1),
                        "vm_size": config.get("vm_size", "Standard_D2s_v3"),
                        "os_type": "Linux",
                        "type": "VirtualMachineScaleSets",
                    }
                ],
                "service_principal_profile": {
                    "client_id": self.config.get("client_id"),
                    "secret": self.config.get("client_secret"),
                },
            }

            poller = self.container_client.managed_clusters.begin_create_or_update(
                resource_group_name=self.resource_group,
                resource_name=f"pulseq-{name}",
                parameters=cluster,
            )

            # Wait for operation to complete
            cluster_result = poller.result()

            return {
                "environment_id": cluster_result.id,
                "status": cluster_result.provisioning_state,
                "endpoint": cluster_result.fqdn,
            }

        except Exception as e:
            logger.error(f"Failed to create test environment: {str(e)}")
            raise

    def destroy_test_environment(self, environment_id: str) -> None:
        """Destroy a test environment in Azure."""
        try:
            # Extract resource group and cluster name from environment_id
            parts = environment_id.split("/")
            resource_group = parts[4]
            cluster_name = parts[8]

            poller = self.container_client.managed_clusters.begin_delete(
                resource_group_name=resource_group, resource_name=cluster_name
            )
            poller.result()

        except Exception as e:
            logger.error(f"Failed to destroy test environment: {str(e)}")
            raise

    def scale_environment(
        self, environment_id: str, scale_config: Dict[str, Any]
    ) -> None:
        """Scale the test environment resources."""
        try:
            # Extract resource group and cluster name from environment_id
            parts = environment_id.split("/")
            resource_group = parts[4]
            cluster_name = parts[8]

            # Get current cluster
            cluster = self.container_client.managed_clusters.get(
                resource_group_name=resource_group, resource_name=cluster_name
            )

            # Update node count
            cluster.agent_pool_profiles[0].count = scale_config.get("node_count", 1)

            poller = self.container_client.managed_clusters.begin_create_or_update(
                resource_group_name=resource_group,
                resource_name=cluster_name,
                parameters=cluster,
            )
            poller.result()

        except Exception as e:
            logger.error(f"Failed to scale environment: {str(e)}")
            raise

    def get_environment_status(self, environment_id: str) -> Dict[str, Any]:
        """Get the status of a test environment."""
        try:
            # Extract resource group and cluster name from environment_id
            parts = environment_id.split("/")
            resource_group = parts[4]
            cluster_name = parts[8]

            cluster = self.container_client.managed_clusters.get(
                resource_group_name=resource_group, resource_name=cluster_name
            )

            return {
                "status": cluster.provisioning_state,
                "node_count": cluster.agent_pool_profiles[0].count,
                "endpoint": cluster.fqdn,
                "version": cluster.kubernetes_version,
            }

        except Exception as e:
            logger.error(f"Failed to get environment status: {str(e)}")
            raise

    def list_environments(self) -> List[Dict[str, Any]]:
        """List all test environments."""
        try:
            clusters = self.container_client.managed_clusters.list_by_resource_group(
                resource_group_name=self.resource_group
            )

            environments = []
            for cluster in clusters:
                if cluster.name.startswith("pulseq-"):
                    environments.append(
                        {
                            "environment_id": cluster.id,
                            "name": cluster.name,
                            "status": cluster.provisioning_state,
                        }
                    )

            return environments

        except Exception as e:
            logger.error(f"Failed to list environments: {str(e)}")
            raise

    def get_cost_estimate(self, environment_id: Optional[str] = None) -> Dict[str, Any]:
        """Get cost estimate for environment(s)."""
        try:
            # This is a simplified cost estimation
            # In a real implementation, you would use Azure Cost Management API
            if environment_id:
                parts = environment_id.split("/")
                resource_group = parts[4]
                cluster_name = parts[8]

                cluster = self.container_client.managed_clusters.get(
                    resource_group_name=resource_group, resource_name=cluster_name
                )
                node_count = cluster.agent_pool_profiles[0].count
                vm_size = cluster.agent_pool_profiles[0].vm_size

                # Example rates (these should be fetched from Azure pricing API)
                hourly_rate = 0.15  # Example rate per node
                estimated_cost = {
                    "hourly": node_count * hourly_rate,
                    "daily": node_count * hourly_rate * 24,
                    "monthly": node_count * hourly_rate * 24 * 30,
                }
            else:
                environments = self.list_environments()
                total_nodes = sum(
                    self.container_client.managed_clusters.get(
                        resource_group_name=env["environment_id"].split("/")[4],
                        resource_name=env["environment_id"].split("/")[8],
                    )
                    .agent_pool_profiles[0]
                    .count
                    for env in environments
                )
                hourly_rate = 0.15  # Example rate per node
                estimated_cost = {
                    "hourly": total_nodes * hourly_rate,
                    "daily": total_nodes * hourly_rate * 24,
                    "monthly": total_nodes * hourly_rate * 24 * 30,
                }

            return estimated_cost

        except Exception as e:
            logger.error(f"Failed to get cost estimate: {str(e)}")
            raise
