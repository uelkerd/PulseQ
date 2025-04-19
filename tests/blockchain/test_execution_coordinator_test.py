import pytest
from src.blockchain.test_execution_coordinator import TestExecutionCoordinator
import os
from dotenv import load_dotenv
import time

load_dotenv()

@pytest.fixture
def coordinator():
    return TestExecutionCoordinator()

@pytest.fixture
def test_job(coordinator):
    test_id = "test_001"
    test_script = "def test_example(): assert True"
    reward = 1000000000000000  # 0.001 ETH in wei
    
    coordinator.create_test_job(test_id, test_script, reward)
    coordinator.accept_test_job(test_id)
    
    result_data = {
        "status": "passed",
        "duration": 1.23,
        "metrics": {
            "cpu_usage": 45.6,
            "memory_usage": 123.4
        }
    }
    coordinator.complete_test_job(test_id, True, result_data)
    
    return test_id

def test_create_and_execute_test_job(coordinator):
    # Create a test job
    test_id = "test_001"
    test_script = "def test_example(): assert True"
    reward = 1000000000000000  # 0.001 ETH in wei
    
    tx_hash = coordinator.create_test_job(test_id, test_script, reward)
    assert tx_hash is not None
    assert len(tx_hash) > 0
    
    # Accept the test job
    accept_tx_hash = coordinator.accept_test_job(test_id)
    assert accept_tx_hash is not None
    
    # Complete the test job with result data
    result_data = {
        "status": "passed",
        "duration": 1.23,
        "metrics": {
            "cpu_usage": 45.6,
            "memory_usage": 123.4
        }
    }
    complete_tx_hash = coordinator.complete_test_job(test_id, True, result_data)
    assert complete_tx_hash is not None
    
    # Verify job details
    job_details = coordinator.get_test_job(test_id)
    assert job_details['test_script'] == test_script
    assert job_details['reward'] == reward
    assert job_details['is_completed'] is True
    assert job_details['result_hash'] is not None

def test_dispute_creation_and_resolution(coordinator, test_job):
    # Create a dispute
    dispute_reason = "Test results appear incorrect"
    dispute_tx_hash = coordinator.create_dispute(test_job, dispute_reason)
    assert dispute_tx_hash is not None
    
    # Verify dispute details
    dispute_details = coordinator.get_dispute(test_job)
    assert dispute_details['reason'] == dispute_reason
    assert dispute_details['is_resolved'] is False
    
    # Add verifiers
    for i in range(3):
        verifier_tx_hash = coordinator.add_verifier(test_job)
        assert verifier_tx_hash is not None
    
    # Vote on dispute
    vote_tx_hash = coordinator.vote_on_dispute(test_job, True)
    assert vote_tx_hash is not None
    
    # Verify dispute resolution
    updated_dispute = coordinator.get_dispute(test_job)
    assert updated_dispute['is_resolved'] is True

def test_result_verification(coordinator):
    test_id = "verification_test"
    test_script = "def test_verification(): assert True"
    reward = 1000000000000000
    
    # Create and complete test with specific result data
    coordinator.create_test_job(test_id, test_script, reward)
    coordinator.accept_test_job(test_id)
    
    result_data = {
        "status": "passed",
        "duration": 1.23,
        "metrics": {
            "cpu_usage": 45.6,
            "memory_usage": 123.4
        }
    }
    coordinator.complete_test_job(test_id, True, result_data)
    
    # Verify result hash
    job_details = coordinator.get_test_job(test_id)
    assert job_details['result_hash'] is not None
    
    # Create dispute with different result data
    coordinator.create_dispute(test_id, "Result data mismatch")
    
    # Verify dispute affects job status
    updated_job = coordinator.get_test_job(test_id)
    assert updated_job['is_disputed'] is True

def test_reputation_system(coordinator):
    test_id = "reputation_test"
    test_script = "def test_reputation(): assert True"
    reward = 1000000000000000
    
    # Initial reputation check
    initial_rep = coordinator.get_executor_reputation(os.getenv('PRIVATE_KEY'))
    
    # Complete successful test
    coordinator.create_test_job(test_id, test_script, reward)
    coordinator.accept_test_job(test_id)
    result_data = {"status": "passed"}
    coordinator.complete_test_job(test_id, True, result_data)
    
    # Verify reputation increase
    updated_rep = coordinator.get_executor_reputation(os.getenv('PRIVATE_KEY'))
    assert updated_rep > initial_rep
    
    # Create and resolve dispute
    coordinator.create_dispute(test_id, "Test quality issue")
    for i in range(3):
        coordinator.add_verifier(test_id)
    coordinator.vote_on_dispute(test_id, True)
    
    # Verify reputation decrease
    final_rep = coordinator.get_executor_reputation(os.getenv('PRIVATE_KEY'))
    assert final_rep < updated_rep

def test_concurrent_test_execution(coordinator):
    test_ids = [f"concurrent_test_{i}" for i in range(3)]
    test_script = "def test_concurrent(): assert True"
    reward = 1000000000000000
    
    # Create multiple test jobs
    for test_id in test_ids:
        coordinator.create_test_job(test_id, test_script, reward)
        coordinator.accept_test_job(test_id)
        result_data = {"status": "passed", "test_id": test_id}
        coordinator.complete_test_job(test_id, True, result_data)
    
    # Verify all jobs completed
    for test_id in test_ids:
        job_details = coordinator.get_test_job(test_id)
        assert job_details['is_completed'] is True
        assert job_details['result_hash'] is not None

def test_error_handling(coordinator):
    # Test invalid test ID
    with pytest.raises(Exception):
        coordinator.get_test_job("nonexistent_test")
    
    # Test duplicate job creation
    test_id = "duplicate_test"
    test_script = "def test_duplicate(): assert True"
    reward = 1000000000000000
    
    coordinator.create_test_job(test_id, test_script, reward)
    with pytest.raises(Exception):
        coordinator.create_test_job(test_id, test_script, reward)
    
    # Test invalid dispute creation
    with pytest.raises(Exception):
        coordinator.create_dispute("nonexistent_test", "Invalid dispute") 