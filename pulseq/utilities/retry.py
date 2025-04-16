# framework/utilities/retry.py
import time
import functools


def retry(max_attempts=3, delay=2, backoff=2):
    """
    Decorator that retries a function call with exponential backoff.
    :param max_attempts: Maximum number of attempts.
    :param delay: Initial delay between attempts in seconds.
    :param backoff: Multiplier applied to the delay on each retry.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            curr_delay = delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"[Retry] {func.__name__} failed on attempt {attempts}: {e}")
                    if attempts >= max_attempts:
                        raise
                    time.sleep(curr_delay)
                    curr_delay *= backoff

        return wrapper

    return decorator


# Example usage:
if __name__ == "__main__":

    @retry(max_attempts=4, delay=1, backoff=2)
    def test_operation():
        print("Attempting operation...")
        raise ValueError("Simulated failure.")

    try:
        test_operation()
    except Exception as e:
        print("Operation ultimately failed:", e)
