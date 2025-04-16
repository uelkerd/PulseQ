# framework/utilities/misc_utils.py

import base64
import logging
import os
import platform
import random
import re
import string
import subprocess
import time
from datetime import datetime
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver

from pulseq.utilities.logger import setup_logger

# Set up module logger
logger = setup_logger("misc_utils")


class MiscUtils:
    """
    Provides miscellaneous utility functions for test automation:
    - Screenshot capture
    - Date and time helpers
    - String manipulation
    - File operations
    - System information
    """

    @staticmethod
    def take_screenshot(driver, filename=None, directory="screenshots"):
        """
        Take a screenshot and save it to a file.

        Args:
            driver: Selenium WebDriver instance
            filename: Screenshot filename (default: timestamp)
            directory: Directory to save screenshot

        Returns:
            str: Path to the saved screenshot
        """
        if not isinstance(driver, WebDriver):
            error_msg = "Driver must be a Selenium WebDriver instance"
            logger.error(error_msg)
            raise TypeError(error_msg)

        # Create directory if it doesn't exist
        Path(directory).mkdir(parents=True, exist_ok=True)

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"screenshot_{timestamp}.png"

        # Ensure filename has .png extension
        if not filename.lower().endswith(".png"):
            filename += ".png"

        file_path = os.path.join(directory, filename)

        try:
            driver.save_screenshot(file_path)
            logger.debug(f"Screenshot saved to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            raise

    @staticmethod
    def get_current_timestamp(format="%Y-%m-%d %H:%M:%S"):
        """
        Get current timestamp formatted as string.

        Args:
            format: Datetime format string

        Returns:
            str: Formatted timestamp
        """
        timestamp = datetime.now().strftime(format)
        logger.debug(f"Current timestamp: {timestamp}")
        return timestamp

    @staticmethod
    def get_formatted_date(days_offset=0, format="%Y-%m-%d"):
        """
        Get a date with optional offset from today.

        Args:
            days_offset: Days to add (positive) or subtract (negative) from today
            format: Date format string

        Returns:
            str: Formatted date
        """
        from datetime import datetime, timedelta

        date = datetime.now() + timedelta(days=days_offset)
        formatted_date = date.strftime(format)
        logger.debug(f"Formatted date with offset {days_offset}: {formatted_date}")
        return formatted_date

    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitize a string for use as a filename.

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        # Replace invalid filename characters with underscores
        sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
        logger.debug(f"Sanitized filename: {sanitized}")
        return sanitized

    @staticmethod
    def create_unique_identifier(prefix="", length=8):
        """
        Create a unique identifier with optional prefix.

        Args:
            prefix: Prefix string
            length: Length of random part

        Returns:
            str: Unique identifier
        """
        chars = string.ascii_lowercase + string.digits
        random_part = "".join(random.choice(chars) for _ in range(length))
        timestamp = int(time.time())

        identifier = f"{prefix}{timestamp}_{random_part}"
        logger.debug(f"Created unique identifier: {identifier}")
        return identifier

    @staticmethod
    def encode_base64(text):
        """
        Encode text to base64.

        Args:
            text: Text to encode

        Returns:
            str: Base64 encoded string
        """
        encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        logger.debug(f"Encoded text to base64")
        return encoded

    @staticmethod
    def decode_base64(encoded_text):
        """
        Decode base64 to text.

        Args:
            encoded_text: Base64 encoded string

        Returns:
            str: Decoded text
        """
        decoded = base64.b64decode(encoded_text).decode("utf-8")
        logger.debug(f"Decoded base64 to text")
        return decoded

    @staticmethod
    def wait(seconds):
        """
        Wait for specified number of seconds.
        CAUTION: Use explicit waits from wait_utils for UI testing instead.
        This is mainly for API testing or other non-UI scenarios.

        Args:
            seconds: Number of seconds to wait
        """
        logger.debug(f"Waiting for {seconds} seconds")
        time.sleep(seconds)

    @staticmethod
    def get_system_info():
        """
        Get system information for test reports.

        Returns:
            dict: System information
        """
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor() or "Unknown",
        }

        logger.debug(f"System info: {info}")
        return info

    @staticmethod
    def compare_images(img1_path, img2_path, threshold=0.1):
        """
        Compare two images and calculate similarity.

        Args:
            img1_path: Path to first image
            img2_path: Path to second image
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            tuple: (is_similar, similarity_score)

        Raises:
            ImportError: If required packages are not installed
        """
        try:
            import numpy as np
            from PIL import Image
            from skimage.metrics import structural_similarity as ssim
        except ImportError:
            error_msg = (
                "Image comparison requires additional packages. "
                "Install with: pip install Pillow numpy scikit-image"
            )
            logger.error(error_msg)
            raise ImportError(error_msg)

        try:
            # Open images
            img1 = Image.open(img1_path).convert("RGB")
            img2 = Image.open(img2_path).convert("RGB")

            # Resize to match dimensions (using the smallest dimensions)
            width = min(img1.width, img2.width)
            height = min(img1.height, img2.height)
            img1 = img1.resize((width, height))
            img2 = img2.resize((width, height))

            # Convert to numpy arrays
            img1_array = np.array(img1)
            img2_array = np.array(img2)

            # Convert to grayscale for SSIM
            img1_gray = np.mean(img1_array, axis=2)
            img2_gray = np.mean(img2_array, axis=2)

            # Calculate SSIM
            similarity, _ = ssim(img1_gray, img2_gray, full=True)
            is_similar = similarity >= (1.0 - threshold)

            logger.debug(
                f"Image similarity: {similarity:.4f}, threshold: {threshold}, similar: {is_similar}"
            )
            return (is_similar, similarity)

        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            raise

    @staticmethod
    def extract_text_from_image(image_path):
        """
        Extract text from an image using OCR.

        Args:
            image_path: Path to image

        Returns:
            str: Extracted text

        Raises:
            ImportError: If pytesseract is not installed
        """
        try:
            import pytesseract
            from PIL import Image
        except ImportError:
            error_msg = (
                "OCR requires additional packages. "
                "Install with: pip install pytesseract Pillow"
            )
            logger.error(error_msg)
            raise ImportError(error_msg)

        try:
            # Open image
            img = Image.open(image_path)

            # Extract text
            text = pytesseract.image_to_string(img)
            logger.debug(f"Extracted text from image: {image_path}")
            return text

        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise

    @staticmethod
    def execute_command(command):
        """
        Execute a system command and return output.

        Args:
            command: Command to execute (string or list)

        Returns:
            tuple: (stdout, stderr, return_code)
        """
        logger.debug(f"Executing command: {command}")

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=isinstance(command, str),
                universal_newlines=True,
            )

            stdout, stderr = process.communicate()
            return_code = process.returncode

            logger.debug(f"Command executed with return code: {return_code}")
            return (stdout, stderr, return_code)

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            raise

    @staticmethod
    def truncate_string(text, max_length=100, suffix="..."):
        """
        Truncate a string to specified length.

        Args:
            text: String to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            str: Truncated string
        """
        if len(text) <= max_length:
            return text

        truncated = text[: max_length - len(suffix)] + suffix
        return truncated

    @staticmethod
    def file_exists(file_path):
        """
        Check if file exists.

        Args:
            file_path: Path to file

        Returns:
            bool: True if file exists
        """
        exists = os.path.isfile(file_path)
        logger.debug(f"File {file_path} exists: {exists}")
        return exists

    @staticmethod
    def directory_exists(directory_path):
        """
        Check if directory exists.

        Args:
            directory_path: Path to directory

        Returns:
            bool: True if directory exists
        """
        exists = os.path.isdir(directory_path)
        logger.debug(f"Directory {directory_path} exists: {exists}")
        return exists


# Example usage
if __name__ == "__main__":
    misc_utils = MiscUtils()

    # Get current timestamp
    timestamp = misc_utils.get_current_timestamp()
    print(f"Current timestamp: {timestamp}")

    # Get tomorrow's date
    tomorrow = misc_utils.get_formatted_date(days_offset=1)
    print(f"Tomorrow's date: {tomorrow}")

    # Create a unique identifier
    unique_id = misc_utils.create_unique_identifier("test_")
    print(f"Unique ID: {unique_id}")

    # Get system information
    system_info = misc_utils.get_system_info()
    print(f"System info: {system_info}")
