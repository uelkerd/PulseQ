export type CloudProvider = "aws" | "gcp" | "azure";

export interface CloudCredentials {
  provider: CloudProvider;
  accessKey: string;
  secretKey: string;
  region: string;
}

export interface CloudResource {
  provider: CloudProvider;
  type: "ec2" | "gce" | "vm";
  id: string;
  configuration: {
    instanceType: string;
    region: string;
    tags: Record<string, string>;
  };
  status: "creating" | "running" | "stopped" | "terminated";
  createdAt: Date;
  updatedAt: Date;
}

export interface CloudStorageConfig {
  provider: CloudProvider;
  bucket: string;
  region: string;
  accessControl: "private" | "public-read" | "public-read-write";
}

export interface CloudMonitoringConfig {
  provider: CloudProvider;
  metrics: string[];
  alarms: {
    metric: string;
    threshold: number;
    period: number;
    evaluationPeriods: number;
  }[];
}

export interface CloudCostEstimate {
  provider: CloudProvider;
  resourceType: string;
  estimatedCost: number;
  currency: string;
  period: "hourly" | "daily" | "monthly";
}
