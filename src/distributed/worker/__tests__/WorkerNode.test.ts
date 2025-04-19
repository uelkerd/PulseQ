import { WorkerNode } from "../WorkerNode";
import { WorkerStatus, TaskStatus } from "../../common/types";
import fetchMock from "jest-fetch-mock";

// Enable fetch mocking
fetchMock.enableMocks();

describe("WorkerNode", () => {
  let worker: WorkerNode;
  const masterUrl = "http://localhost:3000";
  const host = "localhost";
  const port = 8080;
  const capabilities = ["graphql", "performance"];

  beforeEach(() => {
    fetchMock.resetMocks();
    worker = new WorkerNode(masterUrl, host, port, capabilities);
  });

  afterEach(() => {
    worker.shutdown();
  });

  describe("Registration", () => {
    it("should register successfully with master", async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ success: true }));

      const registerPromise = new Promise<void>((resolve) => {
        worker.on("registered", resolve);
      });

      await worker.register();
      await registerPromise;

      expect(fetchMock).toHaveBeenCalledWith(
        `${masterUrl}/register`,
        expect.objectContaining({
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        })
      );
    });

    it("should handle registration failure", async () => {
      fetchMock.mockResponseOnce("", { status: 500 });

      await expect(worker.register()).rejects.toThrow(
        "Failed to register worker"
      );
    });
  });

  describe("Heartbeat", () => {
    it("should send regular heartbeats", async () => {
      fetchMock.mockResponse(JSON.stringify({ success: true }));

      // Wait for two heartbeats
      await new Promise((resolve) => setTimeout(resolve, 11000));

      expect(fetchMock).toHaveBeenCalledTimes(2);
      const calls = fetchMock.mock.calls;
      expect(calls[0][0]).toBe(`${masterUrl}/heartbeat`);
      expect(calls[0][1]?.method).toBe("POST");
    });

    it("should handle heartbeat failures", async () => {
      fetchMock.mockReject(new Error("Network error"));

      const errorPromise = new Promise((resolve) => {
        worker.on("error", resolve);
      });

      // Wait for a heartbeat
      await new Promise((resolve) => setTimeout(resolve, 6000));
      const error = await errorPromise;

      expect(error).toBeDefined();
    });
  });

  describe("Task Execution", () => {
    const taskAssignment = {
      taskId: "test-task-1",
      workerId: "worker-1",
      payload: { test: "data" },
    };

    it("should execute task successfully", async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ success: true })); // For task result

      const taskStartedPromise = new Promise((resolve) => {
        worker.on("taskStarted", resolve);
      });

      const taskCompletedPromise = new Promise((resolve) => {
        worker.on("taskCompleted", resolve);
      });

      await worker.executeTask(taskAssignment);
      const [startedTask, completedResult] = await Promise.all([
        taskStartedPromise,
        taskCompletedPromise,
      ]);

      expect(startedTask).toBeDefined();
      expect(completedResult).toBeDefined();
      expect(completedResult.status).toBe(TaskStatus.COMPLETED);
    });

    it("should handle task execution failure", async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ success: true })); // For task result

      // Mock runTest to throw an error
      jest
        .spyOn(worker as any, "runTest")
        .mockRejectedValue(new Error("Test failed"));

      const taskFailedPromise = new Promise((resolve) => {
        worker.on("taskFailed", resolve);
      });

      await worker.executeTask(taskAssignment);
      const failedResult = await taskFailedPromise;

      expect(failedResult).toBeDefined();
      expect(failedResult.status).toBe(TaskStatus.FAILED);
      expect(failedResult.error).toBe("Test failed");
    });

    it("should not execute task when busy", async () => {
      // Set worker as busy
      (worker as any).status = WorkerStatus.BUSY;

      await expect(worker.executeTask(taskAssignment)).rejects.toThrow(
        "Worker is not idle"
      );
    });
  });

  describe("Status Management", () => {
    it("should return correct status", () => {
      const status = worker.getStatus();

      expect(status.id).toBeDefined();
      expect(status.host).toBe(host);
      expect(status.port).toBe(port);
      expect(status.status).toBe(WorkerStatus.IDLE);
      expect(status.capabilities).toEqual(capabilities);
    });

    it("should update status during task execution", async () => {
      fetchMock.mockResponseOnce(JSON.stringify({ success: true }));

      const taskAssignment = {
        taskId: "test-task-1",
        workerId: "worker-1",
        payload: { test: "data" },
      };

      expect(worker.getStatus().status).toBe(WorkerStatus.IDLE);

      const executionPromise = worker.executeTask(taskAssignment);
      expect(worker.getStatus().status).toBe(WorkerStatus.BUSY);

      await executionPromise;
      expect(worker.getStatus().status).toBe(WorkerStatus.IDLE);
    });
  });

  describe("Shutdown", () => {
    it("should cleanup resources on shutdown", () => {
      const shutdownPromise = new Promise((resolve) => {
        worker.on("shutdown", resolve);
      });

      worker.shutdown();

      expect(worker.getStatus().status).toBe(WorkerStatus.OFFLINE);
      return shutdownPromise;
    });
  });
});
