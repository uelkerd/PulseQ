export interface WorkerRegistration {
  id: string;
  capabilities: string[];
  resources: {
    cpu: number;
    memory: number;
    disk: number;
  };
  status: "idle" | "busy" | "offline";
}

export interface TestTask {
  id: string;
  type: "graphql" | "rest" | "performance";
  priority: number;
  dependencies: string[];
  timeout: number;
  retryCount: number;
  status: "pending" | "running" | "completed" | "failed";
  assignedWorker?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface TaskResult {
  taskId: string;
  workerId: string;
  status: "success" | "failure";
  output: any;
  error?: string;
  duration: number;
  metrics: {
    cpuUsage: number;
    memoryUsage: number;
    networkUsage: number;
  };
}

export interface WorkerHealth {
  workerId: string;
  status: "healthy" | "unhealthy";
  lastHeartbeat: Date;
  metrics: {
    cpuUsage: number;
    memoryUsage: number;
    diskUsage: number;
  };
}
