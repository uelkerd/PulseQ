import {
  WorkerNode as WorkerNodeType,
  WorkerStatus,
  Task,
  TaskStatus,
  TaskResult,
  WorkerRegistration,
  Heartbeat,
  TaskAssignment,
} from "../common/types";
import { EventEmitter } from "events";
import { v4 as uuidv4 } from "uuid";
import { TestExecutor, TestPayload } from "./testExecutor";
import fetch from "node-fetch";

// Add type declarations for Node.js built-ins
declare global {
  namespace NodeJS {
    interface Timeout {}
  }
}

export class WorkerNode extends EventEmitter {
  private id: string;
  private host: string;
  private port: number;
  private status: WorkerStatus;
  private capabilities: string[];
  private currentTask: Task | null;
  private heartbeatInterval: NodeJS.Timeout;
  private masterUrl: string;
  private testExecutor: TestExecutor;

  constructor(
    masterUrl: string,
    host: string,
    port: number,
    capabilities: string[] = []
  ) {
    super();
    this.id = uuidv4();
    this.host = host;
    this.port = port;
    this.status = WorkerStatus.IDLE;
    this.capabilities = capabilities;
    this.currentTask = null;
    this.masterUrl = masterUrl;
    this.testExecutor = new TestExecutor();
    this.startHeartbeat();
  }

  /**
   * Register with the master node
   */
  public async register(): Promise<void> {
    const registration: WorkerRegistration = {
      workerId: this.id,
      host: this.host,
      port: this.port,
      capabilities: this.capabilities,
    };

    try {
      const response = await fetch(`${this.masterUrl}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(registration),
      });

      if (!response.ok) {
        throw new Error(`Failed to register worker: ${response.statusText}`);
      }

      this.emit("registered");
    } catch (error) {
      this.emit("error", error);
      throw error;
    }
  }

  /**
   * Start sending heartbeats to master
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(async () => {
      const heartbeat: Heartbeat = {
        workerId: this.id,
        status: this.status,
        currentTaskId: this.currentTask?.id,
        timestamp: new Date(),
      };

      try {
        const response = await fetch(`${this.masterUrl}/heartbeat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(heartbeat),
        });

        if (!response.ok) {
          throw new Error(`Heartbeat failed: ${response.statusText}`);
        }
      } catch (error) {
        this.emit("error", error);
      }
    }, 5000); // Send heartbeat every 5 seconds
  }

  /**
   * Execute an assigned task
   */
  public async executeTask(assignment: TaskAssignment): Promise<void> {
    if (this.status !== WorkerStatus.IDLE) {
      throw new Error("Worker is not idle");
    }

    this.status = WorkerStatus.BUSY;
    this.currentTask = {
      id: assignment.taskId,
      type: assignment.payload.type,
      payload: assignment.payload,
      priority: 1,
      status: TaskStatus.RUNNING,
      assignedWorker: this.id,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.emit("taskStarted", this.currentTask);

    try {
      // Execute the test using TestExecutor
      const testPayload: TestPayload = {
        type: assignment.payload.type,
        config: assignment.payload.config,
        testCase: assignment.payload.testCase,
      };

      const startTime = Date.now();
      const result = await this.testExecutor.executeTest(testPayload);
      const duration = Date.now() - startTime;

      const taskResult: TaskResult = {
        taskId: assignment.taskId,
        status: result.success ? TaskStatus.COMPLETED : TaskStatus.FAILED,
        result: result.data,
        error: result.error,
        duration,
      };

      await this.sendTaskResult(taskResult);
      this.emit(result.success ? "taskCompleted" : "taskFailed", taskResult);
    } catch (error) {
      const taskResult: TaskResult = {
        taskId: assignment.taskId,
        status: TaskStatus.FAILED,
        error: error instanceof Error ? error.message : "Unknown error",
        duration: 0,
      };

      await this.sendTaskResult(taskResult);
      this.emit("taskFailed", taskResult);
    } finally {
      this.status = WorkerStatus.IDLE;
      this.currentTask = null;
    }
  }

  /**
   * Send task result to master
   */
  private async sendTaskResult(result: TaskResult): Promise<void> {
    try {
      const response = await fetch(`${this.masterUrl}/task-result`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(result),
      });

      if (!response.ok) {
        throw new Error(`Failed to send task result: ${response.statusText}`);
      }
    } catch (error) {
      this.emit("error", error);
      throw error;
    }
  }

  /**
   * Get current worker status
   */
  public getStatus(): WorkerNodeType {
    return {
      id: this.id,
      host: this.host,
      port: this.port,
      status: this.status,
      capabilities: this.capabilities,
      lastHeartbeat: new Date(),
    };
  }

  /**
   * Cleanup resources
   */
  public shutdown(): void {
    clearInterval(this.heartbeatInterval);
    this.status = WorkerStatus.OFFLINE;
    this.emit("shutdown");
  }
}
