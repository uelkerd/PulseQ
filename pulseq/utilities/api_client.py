# pulseq/utilities/api_client.py

import json
import logging
from typing import Dict, Optional, Union

import requests

from pulseq.utilities.retry import retry

logger = logging.getLogger(__name__)


class APIClient:
    """API client for making HTTP requests with retry mechanism."""

    def __init__(self, base_url: str, headers: Optional[Dict] = None):
        """Initialize API client with base URL and optional headers."""
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.session = requests.Session()

    @retry(max_attempts=3, delay=1, backoff=2)
    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict:
        """Make an HTTP request with retry mechanism."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = {**self.headers, **(headers or {})}

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=request_headers,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict:
        """Make a GET request."""
        return self.request("GET", endpoint, params=params, headers=headers)

    def post(
        self,
        endpoint: str,
        data: Dict,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict:
        """Make a POST request."""
        return self.request("POST", endpoint, data=data, params=params, headers=headers)

    def put(
        self,
        endpoint: str,
        data: Dict,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict:
        """Make a PUT request."""
        return self.request("PUT", endpoint, data=data, params=params, headers=headers)

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint, params=params, headers=headers)

    def close(self) -> None:
        """Close the session."""
        self.session.close()
