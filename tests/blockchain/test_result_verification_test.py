import json
import os

import pytest
from dotenv import load_dotenv

from src.blockchain.test_result_verifier import TestResultVerifier

load_dotenv()


@pytest.fixture
def verifier():
    return TestResultVerifier()


def test_store_and_verify_test_result(verifier):
    # Sample test result data
    test_result = {
        "test_id": "test_001",
        "status": "passed",
        "duration": 1.23,
        "metrics": {"cpu_usage": 45.6, "memory_usage": 123.4},
    }

    # Store test result on blockchain
    tx_hash = verifier.store_test_result(test_result["test_id"], test_result)

    assert tx_hash is not None
    assert len(tx_hash) > 0

    # Verify test result
    verified_result = verifier.verify_test_result(test_result["test_id"])

    assert verified_result["test_id"] == test_result["test_id"]
    assert verified_result["status"] == test_result["status"]
    assert verified_result["metrics"] == test_result["metrics"]


def test_get_test_result_history(verifier):
    test_id = "test_002"

    # Store multiple results for the same test
    for i in range(3):
        test_result = {
            "test_id": test_id,
            "status": "passed",
            "iteration": i,
            "timestamp": i,
        }
        verifier.store_test_result(test_id, test_result)

    # Get history
    history = verifier.get_test_result_history(test_id)

    assert len(history) == 3
    for i, result in enumerate(history):
        assert result["test_id"] == test_id
        assert result["iteration"] == i
