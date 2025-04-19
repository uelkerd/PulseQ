from locust import HttpUser, task, between
import random
import string

class TestUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """Initialize test user"""
        self.client.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @task(3)
    def test_graphql_query(self):
        """Test GraphQL query performance"""
        query = """
        query {
            testResults {
                id
                status
                duration
            }
        }
        """
        self.client.post("/graphql", json={"query": query})

    @task(2)
    def test_api_endpoint(self):
        """Test REST API endpoint performance"""
        self.client.get("/api/v1/tests")

    @task(1)
    def test_complex_operation(self):
        """Test complex operation performance"""
        data = {
            "test_id": ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
            "parameters": {
                "complexity": "high",
                "iterations": 1000
            }
        }
        self.client.post("/api/v1/complex-test", json=data)

class DistributedTestUser(TestUser):
    @task(2)
    def test_distributed_operation(self):
        """Test distributed operation performance"""
        data = {
            "operation": "distributed",
            "nodes": 5,
            "workload": "heavy"
        }
        self.client.post("/api/v1/distributed-test", json=data) 