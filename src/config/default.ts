import { CloudProvider } from "../cloud/types";

export const config = {
  distributed: {
    master: {
      port: 3000,
      host: "localhost",
      maxWorkers: 100,
      taskQueueSize: 1000,
      heartbeatInterval: 5000, // 5 seconds
    },
    worker: {
      maxConcurrentTasks: 5,
      resourceCheckInterval: 1000, // 1 second
      taskTimeout: 300000, // 5 minutes
    },
  },
  cloud: {
    defaultProvider: "aws" as CloudProvider,
    regions: {
      aws: ["us-east-1", "us-west-2", "eu-west-1"],
      gcp: ["us-central1", "europe-west1", "asia-east1"],
      azure: ["eastus", "westeurope", "southeastasia"],
    },
    instanceTypes: {
      aws: ["t2.micro", "t2.small", "t2.medium"],
      gcp: ["e2-micro", "e2-small", "e2-medium"],
      azure: ["B1s", "B2s", "B2ms"],
    },
  },
  cache: {
    defaultStrategy: "memory",
    memory: {
      maxSize: 100 * 1024 * 1024, // 100MB
      ttl: 3600, // 1 hour
    },
    redis: {
      host: "localhost",
      port: 6379,
      ttl: 86400, // 24 hours
    },
    file: {
      path: "./cache",
      maxSize: 1024 * 1024 * 1024, // 1GB
    },
  },
  environment: {
    defaultType: "development",
    types: ["development", "staging", "production"],
    resources: {
      development: {
        cpu: 1,
        memory: 1024, // 1GB
        storage: 5120, // 5GB
      },
      staging: {
        cpu: 2,
        memory: 2048, // 2GB
        storage: 10240, // 10GB
      },
      production: {
        cpu: 4,
        memory: 4096, // 4GB
        storage: 20480, // 20GB
      },
    },
  },
  monitoring: {
    metrics: {
      collectionInterval: 1000, // 1 second
      retentionPeriod: 604800, // 7 days
    },
    alerts: {
      defaultSeverity: "warning",
      notificationChannels: ["email", "slack"],
    },
    dashboard: {
      updateInterval: 5000, // 5 seconds
      maxDataPoints: 1000,
    },
  },
};
