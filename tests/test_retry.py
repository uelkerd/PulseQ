# tests/test_retry.py
import pytest

from pulseq.utilities.retry import retry

attempts_log = []


@retry(max_attempts=3, delay=1, backoff=1)
def flaky_operation():
    attempts_log.append("attempt")
    # Simulate failure on the first two attempts, and pass on the third.
    if len(attempts_log) < 3:
        raise Exception("Flaky error!")
    return "Success"


def test_flaky_operation():
    result = flaky_operation()
    assert result == "Success"
    assert len(attempts_log) == 3
