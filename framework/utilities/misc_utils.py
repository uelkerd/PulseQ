import base64
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

from framework.utilities.logger import setup_logger

def get_formatted_date(days_offset=0, format="%Y-%m-%d"):
    """
    Get a date with optional offset from today.

    Args:
        days_offset: Days to add (positive) or subtract (negative) from today
        format: Date format string

    Returns:
        str: Formatted date
    """
    from datetime import timedelta

    date = datetime.now() + timedelta(days=days_offset)
    formatted_date = date.strftime(format)
    return formatted_date 