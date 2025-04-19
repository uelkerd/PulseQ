import logging
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from .base import CloudProvider

logger = logging.getLogger(__name__)


class AWSProvider(CloudProvider):
    """AWS cloud provider implementation."""

    def __init__(self):
        self.ec2 = None
        self.ecs = None
        self.cloudwatch = None
        self.config = None

    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize AWS provider with configuration."""
        self.config = config
        try:
            self.ec2 = boto3.client(
                "ec2",
                region_name=config.get("region", "us-east-1"),
                aws_access_key_id=config.get("access_key"),
                aws_secret_access_key=config.get("secret_key"),
            )
            self.ecs = boto3.client(
                "ecs",
                region_name=config.get("region", "us-east-1"),
                aws_access_key_id=config.get("access_key"),
                aws_secret_access_key=config.get("secret_key"),
            )
            self.cloudwatch = boto3.client(
                "cloudwatch",
                region_name=config.get("region", "us-east-1"),
                aws_access_key_id=config.get("access_key"),
                aws_secret_access_key=config.get("secret_key"),
            )
        except Exception as e:
            logger.error(f"Failed to initialize AWS provider: {str(e)}")
            raise

    def create_test_environment(
        self, name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a test environment in AWS."""
        try:
            # Create ECS cluster
            cluster_response = self.ecs.create_cluster(
                clusterName=f"pulseq-{name}",
                tags=[{"key": "Environment", "value": "test"}],
            )

            # Create task definition
            task_definition = self.ecs.register_task_definition(
                family=f"pulseq-{name}",
                containerDefinitions=[
                    {
                        "name": "test-container",
                        "image": config.get("image", "pulseq/test-runner:latest"),
                        "cpu": config.get("cpu", 256),
                        "memory": config.get("memory", 512),
                        "essential": True,
                    }
                ],
            )

            # Create service
            service = self.ecs.create_service(
                cluster=cluster_response["cluster"]["clusterName"],
                serviceName=f"pulseq-{name}-service",
                taskDefinition=task_definition["taskDefinition"]["taskDefinitionArn"],
                desiredCount=config.get("desired_count", 1),
                launchType="FARGATE",
                networkConfiguration={
                    "awsvpcConfiguration": {
                        "subnets": config.get("subnets", []),
                        "securityGroups": config.get("security_groups", []),
                        "assignPublicIp": "ENABLED",
                    }
                },
            )

            return {
                "environment_id": cluster_response["cluster"]["clusterArn"],
                "status": "CREATING",
                "service_arn": service["service"]["serviceArn"],
            }

        except ClientError as e:
            logger.error(f"AWS API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to create test environment: {str(e)}")
            raise

    def destroy_test_environment(self, environment_id: str) -> None:
        """Destroy a test environment in AWS."""
        try:
            # Delete ECS cluster and all its services
            cluster_name = environment_id.split("/")[-1]
            services = self.ecs.list_services(cluster=cluster_name)["serviceArns"]

            for service in services:
                self.ecs.update_service(
                    cluster=cluster_name, service=service, desiredCount=0
                )
                self.ecs.delete_service(cluster=cluster_name, service=service)

            self.ecs.delete_cluster(cluster=cluster_name)

        except ClientError as e:
            logger.error(f"AWS API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to destroy test environment: {str(e)}")
            raise

    def scale_environment(
        self, environment_id: str, scale_config: Dict[str, Any]
    ) -> None:
        """Scale the test environment resources."""
        try:
            cluster_name = environment_id.split("/")[-1]
            services = self.ecs.list_services(cluster=cluster_name)["serviceArns"]

            for service in services:
                self.ecs.update_service(
                    cluster=cluster_name,
                    service=service,
                    desiredCount=scale_config.get("desired_count", 1),
                )

        except ClientError as e:
            logger.error(f"AWS API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to scale environment: {str(e)}")
            raise

    def get_environment_status(self, environment_id: str) -> Dict[str, Any]:
        """Get the status of a test environment."""
        try:
            cluster_name = environment_id.split("/")[-1]
            cluster = self.ecs.describe_clusters(clusters=[cluster_name])["clusters"][0]

            return {
                "status": cluster["status"],
                "running_tasks": cluster["runningTasksCount"],
                "pending_tasks": cluster["pendingTasksCount"],
                "active_services": cluster["activeServicesCount"],
            }

        except ClientError as e:
            logger.error(f"AWS API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to get environment status: {str(e)}")
            raise

    def list_environments(self) -> List[Dict[str, Any]]:
        """List all test environments."""
        try:
            clusters = self.ecs.list_clusters()["clusterArns"]
            environments = []

            for cluster in clusters:
                cluster_name = cluster.split("/")[-1]
                if cluster_name.startswith("pulseq-"):
                    status = self.get_environment_status(cluster)
                    environments.append(
                        {
                            "environment_id": cluster,
                            "name": cluster_name,
                            "status": status["status"],
                        }
                    )

            return environments

        except ClientError as e:
            logger.error(f"AWS API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to list environments: {str(e)}")
            raise

    def get_cost_estimate(self, environment_id: Optional[str] = None) -> Dict[str, Any]:
        """Get cost estimate for environment(s)."""
        try:
            # This is a simplified cost estimation
            # In a real implementation, you would use AWS Cost Explorer API
            if environment_id:
                cluster_name = environment_id.split("/")[-1]
                status = self.get_environment_status(environment_id)
                estimated_cost = {
                    "hourly": status["running_tasks"] * 0.05,  # Example rate
                    "daily": status["running_tasks"] * 0.05 * 24,
                    "monthly": status["running_tasks"] * 0.05 * 24 * 30,
                }
            else:
                environments = self.list_environments()
                total_tasks = sum(
                    self.get_environment_status(env["environment_id"])["running_tasks"]
                    for env in environments
                )
                estimated_cost = {
                    "hourly": total_tasks * 0.05,
                    "daily": total_tasks * 0.05 * 24,
                    "monthly": total_tasks * 0.05 * 24 * 30,
                }

            return estimated_cost

        except Exception as e:
            logger.error(f"Failed to get cost estimate: {str(e)}")
            raise
