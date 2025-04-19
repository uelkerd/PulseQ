import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.cloud.manager import CloudManager
from src.cloud.providers.aws import AWSProvider
from src.cloud.providers.azure import AzureProvider
from src.cloud.providers.gcp import GCPProvider


@pytest.fixture
def cloud_manager():
    return CloudManager()


@pytest.fixture
def aws_config():
    return {
        "region": "us-east-1",
        "access_key": "test_key",
        "secret_key": "test_secret",
    }


@pytest.fixture
def mock_aws_provider():
    with patch("boto3.client") as mock_client:
        mock_ecs = MagicMock()
        mock_ec2 = MagicMock()
        mock_cloudwatch = MagicMock()

        mock_client.side_effect = [mock_ec2, mock_ecs, mock_cloudwatch]

        yield {"ecs": mock_ecs, "ec2": mock_ec2, "cloudwatch": mock_cloudwatch}


@pytest.fixture
def gcp_config():
    return {
        "project_id": "test-project",
        "zone": "us-central1-a",
        "credentials": {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "test-key",
            "client_email": "test@test.com",
            "client_id": "test-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test%40test.com",
        },
    }


@pytest.fixture
def mock_gcp_cluster():
    return {
        "name": "pulseq-test-cluster",
        "status": "RUNNING",
        "endpoint": "https://test-cluster.endpoint",
        "node_count": 3,
    }


@pytest.fixture
def azure_config():
    return {
        "subscription_id": "test-subscription-id",
        "resource_group": "test-resource-group",
        "location": "eastus",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
    }


@pytest.fixture
def mock_azure_cluster():
    return Mock(
        id="/subscriptions/test-subscription-id/resourceGroups/test-resource-group/providers/Microsoft.ContainerService/managedClusters/pulseq-test-cluster",
        name="pulseq-test-cluster",
        provisioning_state="Succeeded",
        fqdn="test-cluster.eastus.azmk8s.io",
        agent_pool_profiles=[Mock(count=3, vm_size="Standard_D2s_v3")],
        kubernetes_version="1.24.0",
    )


def test_initialize_provider(cloud_manager, aws_config, mock_aws_provider):
    """Test provider initialization."""
    cloud_manager.initialize_provider("aws", aws_config)
    assert cloud_manager.active_provider == "aws"


def test_create_test_environment(cloud_manager, aws_config, mock_aws_provider):
    """Test environment creation."""
    cloud_manager.initialize_provider("aws", aws_config)

    # Mock ECS responses
    mock_aws_provider["ecs"].create_cluster.return_value = {
        "cluster": {
            "clusterArn": "arn:aws:ecs:region:account:cluster/pulseq-test",
            "clusterName": "pulseq-test",
        }
    }

    mock_aws_provider["ecs"].register_task_definition.return_value = {
        "taskDefinition": {
            "taskDefinitionArn": "arn:aws:ecs:region:account:task-definition/pulseq-test:1"
        }
    }

    mock_aws_provider["ecs"].create_service.return_value = {
        "service": {
            "serviceArn": "arn:aws:ecs:region:account:service/pulseq-test-service"
        }
    }

    result = cloud_manager.create_test_environment(
        "test", {"image": "test-image", "cpu": 256, "memory": 512}
    )

    assert result["environment_id"] == "arn:aws:ecs:region:account:cluster/pulseq-test"
    assert result["status"] == "CREATING"


def test_destroy_test_environment(cloud_manager, aws_config, mock_aws_provider):
    """Test environment destruction."""
    cloud_manager.initialize_provider("aws", aws_config)

    # Mock ECS responses
    mock_aws_provider["ecs"].list_services.return_value = {
        "serviceArns": ["arn:aws:ecs:region:account:service/pulseq-test-service"]
    }

    cloud_manager.destroy_test_environment(
        "arn:aws:ecs:region:account:cluster/pulseq-test"
    )

    mock_aws_provider["ecs"].delete_cluster.assert_called_once()


def test_scale_environment(cloud_manager, aws_config, mock_aws_provider):
    """Test environment scaling."""
    cloud_manager.initialize_provider("aws", aws_config)

    # Mock ECS responses
    mock_aws_provider["ecs"].list_services.return_value = {
        "serviceArns": ["arn:aws:ecs:region:account:service/pulseq-test-service"]
    }

    cloud_manager.scale_environment(
        "arn:aws:ecs:region:account:cluster/pulseq-test", {"desired_count": 3}
    )

    mock_aws_provider["ecs"].update_service.assert_called_once()


def test_get_environment_status(cloud_manager, aws_config, mock_aws_provider):
    """Test environment status retrieval."""
    cloud_manager.initialize_provider("aws", aws_config)

    # Mock ECS responses
    mock_aws_provider["ecs"].describe_clusters.return_value = {
        "clusters": [
            {
                "status": "ACTIVE",
                "runningTasksCount": 2,
                "pendingTasksCount": 0,
                "activeServicesCount": 1,
            }
        ]
    }

    status = cloud_manager.get_environment_status(
        "arn:aws:ecs:region:account:cluster/pulseq-test"
    )

    assert status["status"] == "ACTIVE"
    assert status["running_tasks"] == 2


def test_list_environments(cloud_manager, aws_config, mock_aws_provider):
    """Test environment listing."""
    cloud_manager.initialize_provider("aws", aws_config)

    # Mock ECS responses
    mock_aws_provider["ecs"].list_clusters.return_value = {
        "clusterArns": ["arn:aws:ecs:region:account:cluster/pulseq-test"]
    }

    mock_aws_provider["ecs"].describe_clusters.return_value = {
        "clusters": [
            {
                "status": "ACTIVE",
                "runningTasksCount": 2,
                "pendingTasksCount": 0,
                "activeServicesCount": 1,
            }
        ]
    }

    environments = cloud_manager.list_environments()

    assert len(environments) == 1
    assert environments[0]["name"] == "pulseq-test"


def test_get_cost_estimate(cloud_manager, aws_config, mock_aws_provider):
    """Test cost estimation."""
    cloud_manager.initialize_provider("aws", aws_config)

    # Mock ECS responses
    mock_aws_provider["ecs"].describe_clusters.return_value = {
        "clusters": [
            {
                "status": "ACTIVE",
                "runningTasksCount": 2,
                "pendingTasksCount": 0,
                "activeServicesCount": 1,
            }
        ]
    }

    cost = cloud_manager.get_cost_estimate(
        "arn:aws:ecs:region:account:cluster/pulseq-test"
    )

    assert "hourly" in cost
    assert "daily" in cost
    assert "monthly" in cost


def test_initialize_gcp_provider(gcp_config):
    manager = CloudManager()
    with patch("google.cloud.container_v1.ClusterManagerClient") as mock_client:
        manager.initialize_provider("gcp", gcp_config)
        assert manager.active_provider == "gcp"
        assert isinstance(manager._provider_instance, GCPProvider)


def test_create_gcp_test_environment(gcp_config, mock_gcp_cluster):
    manager = CloudManager()
    with patch("google.cloud.container_v1.ClusterManagerClient") as mock_client:
        mock_client.return_value.create_cluster.return_value = Mock(
            name="operations/test-operation"
        )
        mock_client.return_value.get_operation.return_value = Mock(
            status=2,
            error=None,  # DONE
        )
        mock_client.return_value.get_cluster.return_value = mock_gcp_cluster

        manager.initialize_provider("gcp", gcp_config)
        result = manager.create_test_environment(
            "test-cluster", {"node_count": 3, "machine_type": "e2-medium"}
        )

        assert result["environment_id"] == "pulseq-test-cluster"
        assert result["status"] == "RUNNING"
        assert result["endpoint"] == "https://test-cluster.endpoint"


def test_destroy_gcp_test_environment(gcp_config):
    manager = CloudManager()
    with patch("google.cloud.container_v1.ClusterManagerClient") as mock_client:
        mock_client.return_value.delete_cluster.return_value = Mock(
            name="operations/test-operation"
        )
        mock_client.return_value.get_operation.return_value = Mock(
            status=2,
            error=None,  # DONE
        )

        manager.initialize_provider("gcp", gcp_config)
        manager.destroy_test_environment("pulseq-test-cluster")

        mock_client.return_value.delete_cluster.assert_called_once()


def test_scale_gcp_environment(gcp_config):
    manager = CloudManager()
    with patch("google.cloud.container_v1.ClusterManagerClient") as mock_client:
        mock_client.return_value.set_node_pool_size.return_value = Mock(
            name="operations/test-operation"
        )
        mock_client.return_value.get_operation.return_value = Mock(
            status=2,
            error=None,  # DONE
        )

        manager.initialize_provider("gcp", gcp_config)
        manager.scale_environment("pulseq-test-cluster", {"node_count": 5})

        mock_client.return_value.set_node_pool_size.assert_called_once()


def test_get_gcp_environment_status(gcp_config, mock_gcp_cluster):
    manager = CloudManager()
    with patch("google.cloud.container_v1.ClusterManagerClient") as mock_client:
        mock_client.return_value.get_cluster.return_value = mock_gcp_cluster

        manager.initialize_provider("gcp", gcp_config)
        status = manager.get_environment_status("pulseq-test-cluster")

        assert status["status"] == "RUNNING"
        assert status["node_count"] == 3
        assert status["endpoint"] == "https://test-cluster.endpoint"


def test_list_gcp_environments(gcp_config, mock_gcp_cluster):
    manager = CloudManager()
    with patch("google.cloud.container_v1.ClusterManagerClient") as mock_client:
        mock_client.return_value.list_clusters.return_value = [mock_gcp_cluster]

        manager.initialize_provider("gcp", gcp_config)
        environments = manager.list_environments()

        assert len(environments) == 1
        assert environments[0]["id"] == "pulseq-test-cluster"
        assert environments[0]["name"] == "pulseq-test-cluster"
        assert environments[0]["status"] == "RUNNING"


def test_get_gcp_cost_estimate(gcp_config):
    manager = CloudManager()
    with patch("google.cloud.container_v1.ClusterManagerClient") as mock_client:
        mock_client.return_value.get_cluster.return_value = Mock(node_count=3)

        manager.initialize_provider("gcp", gcp_config)
        cost = manager.get_cost_estimate("pulseq-test-cluster")

        assert "hourly" in cost
        assert "daily" in cost
        assert "monthly" in cost


def test_initialize_azure_provider(azure_config):
    manager = CloudManager()
    with patch("azure.identity.DefaultAzureCredential") as mock_credential, patch(
        "azure.mgmt.containerservice.ContainerServiceClient"
    ) as mock_container_client, patch(
        "azure.mgmt.resource.ResourceManagementClient"
    ) as mock_resource_client:
        manager.initialize_provider("azure", azure_config)
        assert manager.active_provider == "azure"
        assert isinstance(manager._provider_instance, AzureProvider)


def test_create_azure_test_environment(azure_config, mock_azure_cluster):
    manager = CloudManager()
    with patch("azure.identity.DefaultAzureCredential") as mock_credential, patch(
        "azure.mgmt.containerservice.ContainerServiceClient"
    ) as mock_container_client:
        mock_container_client.return_value.managed_clusters.begin_create_or_update.return_value = Mock(
            result=lambda: mock_azure_cluster
        )

        manager.initialize_provider("azure", azure_config)
        result = manager.create_test_environment(
            "test-cluster", {"node_count": 3, "vm_size": "Standard_D2s_v3"}
        )

        assert result["environment_id"] == mock_azure_cluster.id
        assert result["status"] == "Succeeded"
        assert result["endpoint"] == "test-cluster.eastus.azmk8s.io"


def test_destroy_azure_test_environment(azure_config):
    manager = CloudManager()
    with patch("azure.identity.DefaultAzureCredential") as mock_credential, patch(
        "azure.mgmt.containerservice.ContainerServiceClient"
    ) as mock_container_client:
        mock_container_client.return_value.managed_clusters.begin_delete.return_value = Mock(
            result=lambda: None
        )

        manager.initialize_provider("azure", azure_config)
        manager.destroy_test_environment(
            "/subscriptions/test-subscription-id/resourceGroups/test-resource-group/providers/Microsoft.ContainerService/managedClusters/pulseq-test-cluster"
        )

        mock_container_client.return_value.managed_clusters.begin_delete.assert_called_once()


def test_scale_azure_environment(azure_config, mock_azure_cluster):
    manager = CloudManager()
    with patch("azure.identity.DefaultAzureCredential") as mock_credential, patch(
        "azure.mgmt.containerservice.ContainerServiceClient"
    ) as mock_container_client:
        mock_container_client.return_value.managed_clusters.get.return_value = (
            mock_azure_cluster
        )
        mock_container_client.return_value.managed_clusters.begin_create_or_update.return_value = Mock(
            result=lambda: mock_azure_cluster
        )

        manager.initialize_provider("azure", azure_config)
        manager.scale_environment(
            "/subscriptions/test-subscription-id/resourceGroups/test-resource-group/providers/Microsoft.ContainerService/managedClusters/pulseq-test-cluster",
            {"node_count": 5},
        )

        mock_container_client.return_value.managed_clusters.begin_create_or_update.assert_called_once()


def test_get_azure_environment_status(azure_config, mock_azure_cluster):
    manager = CloudManager()
    with patch("azure.identity.DefaultAzureCredential") as mock_credential, patch(
        "azure.mgmt.containerservice.ContainerServiceClient"
    ) as mock_container_client:
        mock_container_client.return_value.managed_clusters.get.return_value = (
            mock_azure_cluster
        )

        manager.initialize_provider("azure", azure_config)
        status = manager.get_environment_status(
            "/subscriptions/test-subscription-id/resourceGroups/test-resource-group/providers/Microsoft.ContainerService/managedClusters/pulseq-test-cluster"
        )

        assert status["status"] == "Succeeded"
        assert status["node_count"] == 3
        assert status["endpoint"] == "test-cluster.eastus.azmk8s.io"


def test_list_azure_environments(azure_config, mock_azure_cluster):
    manager = CloudManager()
    with patch("azure.identity.DefaultAzureCredential") as mock_credential, patch(
        "azure.mgmt.containerservice.ContainerServiceClient"
    ) as mock_container_client:
        mock_container_client.return_value.managed_clusters.list_by_resource_group.return_value = [
            mock_azure_cluster
        ]

        manager.initialize_provider("azure", azure_config)
        environments = manager.list_environments()

        assert len(environments) == 1
        assert environments[0]["id"] == mock_azure_cluster.id
        assert environments[0]["name"] == "pulseq-test-cluster"
        assert environments[0]["status"] == "Succeeded"


def test_get_azure_cost_estimate(azure_config, mock_azure_cluster):
    manager = CloudManager()
    with patch("azure.identity.DefaultAzureCredential") as mock_credential, patch(
        "azure.mgmt.containerservice.ContainerServiceClient"
    ) as mock_container_client:
        mock_container_client.return_value.managed_clusters.get.return_value = (
            mock_azure_cluster
        )

        manager.initialize_provider("azure", azure_config)
        cost = manager.get_cost_estimate(
            "/subscriptions/test-subscription-id/resourceGroups/test-resource-group/providers/Microsoft.ContainerService/managedClusters/pulseq-test-cluster"
        )

        assert "hourly" in cost
        assert "daily" in cost
        assert "monthly" in cost
