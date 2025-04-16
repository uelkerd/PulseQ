# framework/config.py
import json
import os

def load_config(config_file="config.json"):
    # Check if config file exists, if not use defaults.
    if not os.path.exists(config_file):
        default_config = {
            "base_url": "http://example.com",
            "timeout": 30,
            "retry_attempts": 3
            # Add more default parameters as needed
        }
        return default_config

    with open(config_file, "r") as file:
        config = json.load(file)
    return config
