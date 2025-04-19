import logging
from typing import Any, Dict, List, Optional

from google.api_core.exceptions import GoogleAPICallError
from google.cloud import compute_v1, container_v1, monitoring_v3

from .base import CloudProvider

logger = logging.getLogger(__name__)


class GCPProvider(CloudProvider):
    """GCP cloud provider implementation."""

    def __init__(self):
        self.compute_client = None
        self.container_client = None
        self.monitoring_client = None
        self.config = None

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize GCP provider with configuration."""
        self.config = config
        try:
            # Initialize GCP clients
            self.compute_client = compute_v1.InstancesClient()
            self.container_client = container_v1.ClusterManagerClient()
            self.monitoring_client = monitoring_v3.MetricServiceClient()

            # Set project and zone
            self.project = config.get("project_id")
            self.zone = config.get("zone", "us-central1-a")

        except Exception as e:
            logger.error(f"Failed to initialize GCP provider: {str(e)}")
            raise

    def create_test_environment(
        self, name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a test environment in GCP."""
        try:
            # Create GKE cluster
            cluster = {
                "name": f"pulseq-{name}",
                "initial_node_count": config.get("node_count", 1),
                "node_config": {
                    "machine_type": config.get("machine_type", "e2-medium"),
                    "disk_size_gb": config.get("disk_size", 100),
                    "oauth_scopes": [
                        "https://www.googleapis.com/auth/devstorage.read_only",
                        "https://www.googleapis.com/auth/logging.write",
                        "https://www.googleapis.com/auth/monitoring",
                    ],
                },
            }

            operation = self.container_client.create_cluster(
                parent=f"projects/{self.project}/locations/{self.zone}", cluster=cluster
            )

            # Wait for operation to complete
            operation.result()

            # Get cluster details
            cluster = self.container_client.get_cluster(
                name=f"projects/{self.project}/locations/{self.zone}/clusters/pulseq-{name}"
            )

            return {
                "environment_id": cluster.name,
                "status": cluster.status.name,
                "endpoint": cluster.endpoint,
            }

        except GoogleAPICallError as e:
            logger.error(f"GCP API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to create test environment: {str(e)}")
            raise

    def destroy_test_environment(self, environment_id: str) -> None:
        """Destroy a test environment in GCP."""
        try:
            operation = self.container_client.delete_cluster(name=environment_id)
            operation.result()

        except GoogleAPICallError as e:
            logger.error(f"GCP API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to destroy test environment: {str(e)}")
            raise

    def scale_environment(
        self, environment_id: str, scale_config: Dict[str, Any]
    ) -> None:
        """Scale the test environment resources."""
        try:
            node_pool = {
                "name": "default-pool",
                "initial_node_count": scale_config.get("node_count", 1),
            }

            operation = self.container_client.set_node_pool_size(
                name=f"{environment_id}/nodePools/default-pool",
                node_count=scale_config.get("node_count", 1),
            )
            operation.result()

        except GoogleAPICallError as e:
            logger.error(f"GCP API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to scale environment: {str(e)}")
            raise

    def get_environment_status(self, environment_id: str) -> Dict[str, Any]:
        """Get the status of a test environment."""
        try:
            cluster = self.container_client.get_cluster(name=environment_id)

            return {
                "status": cluster.status.name,
                "node_count": cluster.current_node_count,
                "endpoint": cluster.endpoint,
                "version": cluster.current_master_version,
            }

        except GoogleAPICallError as e:
            logger.error(f"GCP API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to get environment status: {str(e)}")
            raise

    def list_environments(self) -> List[Dict[str, Any]]:
        """List all test environments."""
        try:
            clusters = self.container_client.list_clusters(
                parent=f"projects/{self.project}/locations/{self.zone}"
            )

            environments = []
            for cluster in clusters:
                if cluster.name.startswith("pulseq-"):
                    environments.append(
                        {
                            "environment_id": cluster.name,
                            "name": cluster.name.split("/")[-1],
                            "status": cluster.status.name,
                        }
                    )

            return environments

        except GoogleAPICallError as e:
            logger.error(f"GCP API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to list environments: {str(e)}")
            raise

    def get_cost_estimate(self, environment_id: Optional[str] = None) -> Dict[str, Any]:
        """Get cost estimate for environment(s)."""
        try:
            # This is a simplified cost estimation
            # In a real implementation, you would use GCP Billing API
            if environment_id:
                cluster = self.container_client.get_cluster(name=environment_id)
                node_count = cluster.current_node_count
                machine_type = cluster.node_config.machine_type

                # Example rates (these should be fetched from GCP pricing API)
                hourly_rate = 0.10  # Example rate per node
                estimated_cost = {
                    "hourly": node_count * hourly_rate,
                    "daily": node_count * hourly_rate * 24,
                    "monthly": node_count * hourly_rate * 24 * 30,
                }
            else:
                environments = self.list_environments()
                total_nodes = sum(
                    self.container_client.get_cluster(
                        name=env["environment_id"]
                    ).current_node_count
                    for env in environments
                )
                hourly_rate = 0.10  # Example rate per node
                estimated_cost = {
                    "hourly": total_nodes * hourly_rate,
                    "daily": total_nodes * hourly_rate * 24,
                    "monthly": total_nodes * hourly_rate * 24 * 30,
                }

            return estimated_cost

        except Exception as e:
            logger.error(f"Failed to get cost estimate: {str(e)}")
            raise
