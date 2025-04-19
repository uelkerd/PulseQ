export interface WorkerNode {
  id: string;
  host: string;
  port: number;
  status: WorkerStatus;
  capabilities: string[];
  lastHeartbeat: Date;
}

export enum WorkerStatus {
  IDLE = "IDLE",
  BUSY = "BUSY",
  OFFLINE = "OFFLINE",
}

export interface Task {
  id: string;
  type: string;
  payload: any;
  priority: number;
  status: TaskStatus;
  assignedWorker?: string;
  createdAt: Date;
  updatedAt: Date;
}

export enum TaskStatus {
  PENDING = "PENDING",
  ASSIGNED = "ASSIGNED",
  RUNNING = "RUNNING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
}

export interface TaskResult {
  taskId: string;
  status: TaskStatus;
  result?: any;
  error?: string;
  duration: number;
}

export interface WorkerRegistration {
  workerId: string;
  host: string;
  port: number;
  capabilities: string[];
}

export interface Heartbeat {
  workerId: string;
  status: WorkerStatus;
  currentTaskId?: string;
  timestamp: Date;
}

export interface TaskAssignment {
  taskId: string;
  workerId: string;
  payload: any;
}
