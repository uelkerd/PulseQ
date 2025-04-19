import {
  WorkerNode,
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

export class MasterNode extends EventEmitter {
  private workers: Map<string, WorkerNode>;
  private tasks: Map<string, Task>;
  private taskQueue: string[];
  private healthCheckInterval: NodeJS.Timeout;

  constructor() {
    super();
    this.workers = new Map();
    this.tasks = new Map();
    this.taskQueue = [];
    this.startHealthMonitoring();
  }

  /**
   * Register a new worker node
   */
  public registerWorker(registration: WorkerRegistration): WorkerNode {
    const worker: WorkerNode = {
      id: registration.workerId,
      host: registration.host,
      port: registration.port,
      status: WorkerStatus.IDLE,
      capabilities: registration.capabilities,
      lastHeartbeat: new Date(),
    };

    this.workers.set(worker.id, worker);
    this.emit("workerRegistered", worker);
    return worker;
  }

  /**
   * Process worker heartbeat
   */
  public processHeartbeat(heartbeat: Heartbeat): void {
    const worker = this.workers.get(heartbeat.workerId);
    if (!worker) {
      throw new Error(`Worker ${heartbeat.workerId} not found`);
    }

    worker.status = heartbeat.status;
    worker.lastHeartbeat = heartbeat.timestamp;

    if (heartbeat.status === WorkerStatus.IDLE) {
      this.assignNextTask(worker);
    }
  }

  /**
   * Submit a new task for execution
   */
  public submitTask(
    taskType: string,
    payload: any,
    priority: number = 1
  ): string {
    const task: Task = {
      id: uuidv4(),
      type: taskType,
      payload,
      priority,
      status: TaskStatus.PENDING,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    this.tasks.set(task.id, task);
    this.taskQueue.push(task.id);
    this.taskQueue.sort((a, b) => {
      const taskA = this.tasks.get(a)!;
      const taskB = this.tasks.get(b)!;
      return taskB.priority - taskA.priority;
    });

    this.emit("taskSubmitted", task);
    this.assignNextTask();
    return task.id;
  }

  /**
   * Process task result from worker
   */
  public processTaskResult(result: TaskResult): void {
    const task = this.tasks.get(result.taskId);
    if (!task) {
      throw new Error(`Task ${result.taskId} not found`);
    }

    task.status = result.status;
    task.updatedAt = new Date();

    if (
      result.status === TaskStatus.COMPLETED ||
      result.status === TaskStatus.FAILED
    ) {
      const worker = this.workers.get(task.assignedWorker!);
      if (worker) {
        worker.status = WorkerStatus.IDLE;
        this.assignNextTask(worker);
      }
    }

    this.emit("taskCompleted", { task, result });
  }

  /**
   * Start health monitoring of workers
   */
  private startHealthMonitoring(): void {
    this.healthCheckInterval = setInterval(() => {
      const now = new Date();
      for (const [workerId, worker] of this.workers.entries()) {
        const timeSinceLastHeartbeat =
          now.getTime() - worker.lastHeartbeat.getTime();
        if (timeSinceLastHeartbeat > 30000) {
          // 30 seconds timeout
          worker.status = WorkerStatus.OFFLINE;
          this.emit("workerOffline", worker);

          // Reassign tasks from offline worker
          for (const task of this.tasks.values()) {
            if (
              task.assignedWorker === workerId &&
              (task.status === TaskStatus.ASSIGNED ||
                task.status === TaskStatus.RUNNING)
            ) {
              task.status = TaskStatus.PENDING;
              task.assignedWorker = undefined;
              this.taskQueue.push(task.id);
            }
          }
        }
      }
    }, 10000); // Check every 10 seconds
  }

  /**
   * Assign next available task to worker
   */
  private assignNextTask(worker?: WorkerNode): void {
    if (!worker) {
      worker = Array.from(this.workers.values()).find(
        (w) => w.status === WorkerStatus.IDLE
      );
      if (!worker) return;
    }

    if (worker.status !== WorkerStatus.IDLE) return;

    const taskId = this.taskQueue.shift();
    if (!taskId) return;

    const task = this.tasks.get(taskId)!;
    task.status = TaskStatus.ASSIGNED;
    task.assignedWorker = worker.id;
    task.updatedAt = new Date();

    worker.status = WorkerStatus.BUSY;

    const assignment: TaskAssignment = {
      taskId: task.id,
      workerId: worker.id,
      payload: task.payload,
    };

    this.emit("taskAssigned", assignment);
  }

  /**
   * Get current status of all workers
   */
  public getWorkerStatus(): WorkerNode[] {
    return Array.from(this.workers.values());
  }

  /**
   * Get current status of all tasks
   */
  public getTaskStatus(): Task[] {
    return Array.from(this.tasks.values());
  }

  /**
   * Cleanup resources
   */
  public shutdown(): void {
    clearInterval(this.healthCheckInterval);
    this.workers.clear();
    this.tasks.clear();
    this.taskQueue = [];
  }
}
