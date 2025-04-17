# framework/utilities/data_handler.py

import csv
import datetime
import json
import os
import random
import string
from pathlib import Path

from pulseq.utilities.logger import setup_logger

# Set up module logger
logger = setup_logger("data_handler")


class DataHandler:
    """
    Handles test data loading and generation for test scenarios.
    Supports JSON, CSV data formats and random data generation.
    """

    def __init__(self, data_folder="test_data"):
        """
        Initialize the data handler with a data folder path.

        Args:
            data_folder: Relative path to the test data folder
        """
        self.data_folder = data_folder
        # Create the data folder if it doesn't exist
        Path(data_folder).mkdir(parents=True, exist_ok=True)
        logger.debug(
            f"Initialized DataHandler with data folder: {data_folder}")

    def load_json_data(self, file_name):
        """
        Load data from a JSON file.

        Args:
            file_name: Name of the JSON file in the data folder

        Returns:
            dict: Data from the JSON file

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the JSON format is invalid
        """
        file_path = os.path.join(self.data_folder, file_name)
        try:
            logger.debug(f"Loading JSON data from {file_path}")
            with open(file_path, "r") as f:
                data = json.load(f)
            logger.debug(
                f"Successfully loaded JSON data with {len(data) if isinstance(data, list) else 'dict'} format"
            )
            return data
        except FileNotFoundError:
            logger.error(f"JSON file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {file_path}: {e}")
            raise

    def save_json_data(self, data, file_name):
        """
        Save data to a JSON file.

        Args:
            data: Data to save (must be JSON serializable)
            file_name: Name of the JSON file in the data folder

        Returns:
            bool: True if successful

        Raises:
            TypeError: If the data is not JSON serializable
        """
        file_path = os.path.join(self.data_folder, file_name)
        try:
            logger.debug(f"Saving JSON data to {file_path}")
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            logger.debug(f"Successfully saved JSON data to {file_path}")
            return True
        except TypeError as e:
            logger.error(f"Data is not JSON serializable: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving JSON data to {file_path}: {e}")
            raise

    def load_csv_data(self, file_name, delimiter=","):
        """
        Load data from a CSV file.

        Args:
            file_name: Name of the CSV file in the data folder
            delimiter: CSV delimiter character

        Returns:
            list: List of dictionaries for each row in the CSV

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        file_path = os.path.join(self.data_folder, file_name)
        try:
            logger.debug(f"Loading CSV data from {file_path}")
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                data = list(reader)
            logger.debug(f"Successfully loaded CSV data with {len(data)} rows")
            return data
        except FileNotFoundError:
            logger.error(f"CSV file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV data from {file_path}: {e}")
            raise

    def save_csv_data(self, data, file_name, delimiter=","):
        """
        Save data to a CSV file.

        Args:
            data: List of dictionaries to save as CSV rows
            file_name: Name of the CSV file in the data folder
            delimiter: CSV delimiter character

        Returns:
            bool: True if successful

        Raises:
            ValueError: If data is not a list of dictionaries
        """
        if not isinstance(data, list) or not all(
            isinstance(item, dict) for item in data
        ):
            error_msg = "Data must be a list of dictionaries"
            logger.error(error_msg)
            raise ValueError(error_msg)

        file_path = os.path.join(self.data_folder, file_name)
        try:
            logger.debug(f"Saving CSV data to {file_path}")

            # Get fieldnames from the first dictionary
            fieldnames = data[0].keys() if data else []

            with open(file_path, "w", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(data)

            logger.debug(
                f"Successfully saved CSV data with {len(data)} rows to {file_path}"
            )
            return True
        except Exception as e:
            logger.error(f"Error saving CSV data to {file_path}: {e}")
            raise

    @staticmethod
    def generate_random_string(length=10, include_digits=True, include_special=False):
        """
        Generate a random string.

        Args:
            length: Length of the string
            include_digits: Whether to include digits
            include_special: Whether to include special characters

        Returns:
            str: Random string
        """
        chars = string.ascii_letters
        if include_digits:
            chars += string.digits
        if include_special:
            chars += string.punctuation

        random_string = "".join(random.choice(chars) for _ in range(length))
        logger.debug(f"Generated random string: {random_string}")
        return random_string

    def generate_random_email(self, domain="example.com"):
        """
        Generate a random email address.

        Args:
            domain: Domain name for the email

        Returns:
            str: Random email address
        """
        username = self.generate_random_string(
            8, include_digits=True, include_special=False
        ).lower()
        email = f"{username}@{domain}"
        logger.debug(f"Generated random email: {email}")
        return email

    @staticmethod
    def generate_random_phone(format="+1-###-###-####"):
        """
        Generate a random phone number.

        Args:
            format: Format string with # as placeholders for digits

        Returns:
            str: Random phone number in the specified format
        """
        phone = ""
        for char in format:
            if char == "#":
                phone += random.choice(string.digits)
            else:
                phone += char

        logger.debug(f"Generated random phone: {phone}")
        return phone

    @staticmethod
    def generate_random_date(start_date=None, end_date=None, date_format="%Y-%m-%d"):
        """
        Generate a random date between start_date and end_date.

        Args:
            start_date: Start date as string in date_format (default: 10 years ago)
            end_date: End date as string in date_format (default: today)
            date_format: Date format string

        Returns:
            str: Random date in the specified format
        """
        if start_date is None:
            # Default to 10 years ago
            start = datetime.datetime.now() - datetime.timedelta(days=365 * 10)
        else:
            start = datetime.datetime.strptime(start_date, date_format)

        if end_date is None:
            # Default to today
            end = datetime.datetime.now()
        else:
            end = datetime.datetime.strptime(end_date, date_format)

        # Generate a random date between start and end
        time_between_dates = end - start
        days_between_dates = time_between_dates.days
        random_days = random.randrange(days_between_dates)
        random_date = start + datetime.timedelta(days=random_days)

        formatted_date = random_date.strftime(date_format)
        logger.debug(f"Generated random date: {formatted_date}")
        return formatted_date

    def generate_test_data_set(self, size=1, template=None):
        """
        Generate a dataset of random test data.

        Args:
            size: Number of data items to generate
            template: Dictionary template with field names and data types
                     (supported types: 'string', 'email', 'phone', 'date', 'number')

        Returns:
            list: List of dictionaries with random test data
        """
        if template is None:
            template = {
                "name": "string",
                "email": "email",
                "phone": "phone",
                "birth_date": "date",
                "id": "number",
            }

        dataset = []

        for i in range(size):
            item = {}
            for field, field_type in template.items():
                if field_type == "string":
                    item[field] = self.generate_random_string()
                elif field_type == "email":
                    item[field] = self.generate_random_email()
                elif field_type == "phone":
                    item[field] = self.generate_random_phone()
                elif field_type == "date":
                    item[field] = self.generate_random_date()
                elif field_type == "number":
                    item[field] = random.randint(1000, 9999)
                else:
                    # Default to string for unknown types
                    item[field] = self.generate_random_string()

            dataset.append(item)

        logger.debug(f"Generated dataset with {size} items")
        return dataset


# Example usage
if __name__ == "__main__":
    data_handler = DataHandler()

    # Generate a dataset
    test_users = data_handler.generate_test_data_set(3)
    print("Generated test users:", test_users)

    # Save to JSON
    data_handler.save_json_data(test_users, "test_users.json")

    # Read from JSON
    loaded_users = data_handler.load_json_data("test_users.json")
    print("Loaded test users:", loaded_users)
