# framework/config.py
import json
import os


def load_config(config_file="config.json"):
    # Load default configuration from file if available, otherwise use defaults.
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config = json.load(file)
    else:
        config = {"base_url": "http://example.com", "timeout": 30, "retry_attempts": 3}

    # Override with environment variables if defined
    config["base_url"] = os.getenv("BASE_URL", config["base_url"])
    config["timeout"] = int(os.getenv("TIMEOUT", config["timeout"]))
    config["retry_attempts"] = int(
        os.getenv("RETRY_ATTEMPTS", config["retry_attempts"])
    )

    return config


if __name__ == "__main__":
    cfg = load_config()
    print("Loaded configuration:", cfg)
