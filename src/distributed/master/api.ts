import express from "express";
import { MasterNode } from "./MasterNode";
import { WorkerRegistration, Heartbeat, TaskResult } from "../common/types";

export class MasterNodeAPI {
  private app: express.Application;
  private masterNode: MasterNode;

  constructor(masterNode: MasterNode) {
    this.masterNode = masterNode;
    this.app = express();
    this.app.use(express.json());
    this.setupRoutes();
  }

  private setupRoutes(): void {
    // Worker registration
    this.app.post("/register", (req, res) => {
      try {
        const registration: WorkerRegistration = req.body;
        const worker = this.masterNode.registerWorker(registration);
        res.json(worker);
      } catch (error) {
        res.status(400).json({ error: error.message });
      }
    });

    // Worker heartbeat
    this.app.post("/heartbeat", (req, res) => {
      try {
        const heartbeat: Heartbeat = req.body;
        this.masterNode.processHeartbeat(heartbeat);
        res.json({ success: true });
      } catch (error) {
        res.status(400).json({ error: error.message });
      }
    });

    // Task result submission
    this.app.post("/task-result", (req, res) => {
      try {
        const result: TaskResult = req.body;
        this.masterNode.processTaskResult(result);
        res.json({ success: true });
      } catch (error) {
        res.status(400).json({ error: error.message });
      }
    });

    // Get worker status
    this.app.get("/workers", (req, res) => {
      const workers = this.masterNode.getWorkerStatus();
      res.json(workers);
    });

    // Get task status
    this.app.get("/tasks", (req, res) => {
      const tasks = this.masterNode.getTaskStatus();
      res.json(tasks);
    });

    // Submit new task
    this.app.post("/tasks", (req, res) => {
      try {
        const { type, payload, priority } = req.body;
        const taskId = this.masterNode.submitTask(type, payload, priority);
        res.json({ taskId });
      } catch (error) {
        res.status(400).json({ error: error.message });
      }
    });
  }

  public start(port: number): void {
    this.app.listen(port, () => {
      console.log(`Master node API listening on port ${port}`);
    });
  }

  public shutdown(): void {
    this.masterNode.shutdown();
  }
}
