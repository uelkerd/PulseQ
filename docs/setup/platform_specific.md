# Platform-Specific Setup Guide

This guide provides detailed setup instructions for various platforms and environments.

## Table of Contents

- [Windows Subsystem for Linux (WSL)](#windows-subsystem-for-linux-wsl)
- [Kubernetes](#kubernetes)
- [AWS ECS](#aws-ecs)
- [Google Cloud Run](#google-cloud-run)
- [Azure Container Instances](#azure-container-instances)
- [CI/CD Platforms](#cicd-platforms)

## Windows Subsystem for Linux (WSL)

### Prerequisites

- Windows 10/11 with WSL 2 installed
- Ubuntu 20.04 LTS or later

### Installation Steps

1. **Enable WSL 2**

   ```powershell
   wsl --set-default-version 2
   ```

2. **Install Ubuntu**

   ```powershell
   wsl --install -d Ubuntu
   ```

3. **Update System**

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Install Dependencies**

   ```bash
   sudo apt install -y python3-pip python3-venv git build-essential
   ```

5. **Setup Python Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

6. **Configure X Server (for GUI tests)**
   ```bash
   # Install VcXsrv on Windows
   # Add to ~/.bashrc:
   export DISPLAY=:0
   ```

## Kubernetes

### Prerequisites

- kubectl
- Helm
- Access to a Kubernetes cluster

### Installation Steps

1. **Create Namespace**

   ```bash
   kubectl create namespace pulseq
   ```

2. **Install with Helm**

   ```bash
   helm install pulseq ./helm \
     --namespace pulseq \
     --set master.replicas=2 \
     --set worker.replicas=5 \
     --set storage.type=persistent
   ```

3. **Verify Installation**

   ```bash
   kubectl get pods -n pulseq
   kubectl get services -n pulseq
   ```

4. **Access Dashboard**
   ```bash
   kubectl port-forward svc/pulseq-dashboard 8080:80 -n pulseq
   ```

### Configuration

```yaml
# values.yaml
master:
  replicas: 2
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 1Gi

worker:
  replicas: 5
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

storage:
  type: persistent
  size: 10Gi
```

## AWS ECS

### Prerequisites

- AWS CLI
- ECS CLI
- Docker

### Installation Steps

1. **Create ECS Cluster**

   ```bash
   aws ecs create-cluster --cluster-name pulseq
   ```

2. **Create Task Definition**

   ```bash
   aws ecs register-task-definition --cli-input-json file://task-definition.json
   ```

3. **Create Service**
   ```bash
   aws ecs create-service \
     --cluster pulseq \
     --service-name pulseq-service \
     --task-definition pulseq:1 \
     --desired-count 3 \
     --launch-type FARGATE
   ```

### Configuration

```json
// task-definition.json
{
  "family": "pulseq",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "pulseq",
      "image": "pulseq:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

## Google Cloud Run

### Prerequisites

- gcloud CLI
- Docker

### Installation Steps

1. **Build and Push Container**

   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/pulseq
   ```

2. **Deploy Service**

   ```bash
   gcloud run deploy pulseq \
     --image gcr.io/PROJECT_ID/pulseq \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Configure Auto-scaling**
   ```bash
   gcloud run services update pulseq \
     --min-instances 1 \
     --max-instances 10 \
     --cpu 1 \
     --memory 2Gi
   ```

## Azure Container Instances

### Prerequisites

- Azure CLI
- Docker

### Installation Steps

1. **Create Resource Group**

   ```bash
   az group create --name pulseq-rg --location eastus
   ```

2. **Create Container Instance**

   ```bash
   az container create \
     --resource-group pulseq-rg \
     --name pulseq \
     --image pulseq:latest \
     --ports 8080 \
     --cpu 1 \
     --memory 2
   ```

3. **Configure Auto-scaling**
   ```bash
   az monitor autoscale create \
     --resource-group pulseq-rg \
     --resource pulseq \
     --resource-type Microsoft.ContainerInstance/containerGroups \
     --name pulseq-autoscale \
     --min-count 1 \
     --max-count 10 \
     --count 1
   ```

## CI/CD Platforms

### GitHub Actions

```yaml
# .github/workflows/pulseq.yml
name: PulseQ CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.8"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
      - name: Run tests
        run: |
          pytest
```

### GitLab CI

```yaml
# .gitlab-ci.yml
image: python:3.8

stages:
  - test
  - deploy

test:
  stage: test
  script:
    - pip install -e .
    - pytest

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
  only:
    - main
```

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'pip install -e .'
                sh 'pytest'
            }
        }
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'echo "Deploy to production"'
            }
        }
    }
}
```

## Next Steps

- [Configuration Guide](../configuration/README.md)
- [Monitoring Setup](../monitoring/README.md)
- [Security Best Practices](../security/README.md)
