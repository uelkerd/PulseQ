# framework/utilities/logger.py

import logging
import os

def setup_logger(name=__name__, log_file="framework.log", level=logging.DEBUG):
    """Set up a logger for the application."""
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create file handler which logs even debug messages
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Example usage:
if __name__ == "__main__":
    logger = setup_logger("my_test_logger")
    logger.debug("This is a debug message")
