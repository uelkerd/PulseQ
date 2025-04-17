# pulseq/utilities/api_client.py

import json
import time

import requests

from pulseq.utilities.logger import setup_logger
from pulseq.utilities.retry import retry

# Set up module logger
logger = setup_logger("api_client")


class APIClient:
    """
    API client for making HTTP requests with advanced features like:
    - Session management
    - Request/response logging
    - Automatic retries
    - Authentication handling
    - Response validation
    """

    def __init__(self, base_url, headers=None, timeout=30, verify_ssl=True):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for all API requests
            headers: Default headers to include in all requests
            timeout: Default request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        logger.debug(f"Initialized API client with base URL: {self.base_url}")

    def _build_url(self, endpoint):
        """
        Build a full URL from the endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            str: Full URL
        """
        # Handle cases where endpoint might already start with /
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    @staticmethod
    def _log_request(method, url, **kwargs):
        """
        Log request details.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Request parameters
        """
        headers = kwargs.get("headers", {})
        # Sanitize headers to avoid logging sensitive information
        sanitized_headers = {}
        for key, value in headers.items():
            if key.lower() in ["authorization", "api-key", "token"]:
                sanitized_headers[key] = "********"
            else:
                sanitized_headers[key] = value

        data = kwargs.get("data")
        if data and isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass

        params = kwargs.get("params")

        logger.debug(f"API Request: {method} {url}")
        logger.debug(f"Headers: {sanitized_headers}")

        if params:
            logger.debug(f"Query Parameters: {params}")

        if data:
            logger.debug(f"Request Body: {data}")

    @staticmethod
    def _log_response(response):
        """
        Log response details.

        Args:
            response: Response object
        """
        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Response Headers: {dict(response.headers)}")

        try:
            if response.text:
                # Try to parse as JSON first
                try:
                    content = response.json()
                    # Truncate large responses to avoid excessive logging
                    content_str = str(content)
                    if len(content_str) > 1000:
                        logger.debug(
                            f"Response Body (truncated): {content_str[:1000]}..."
                        )
                    else:
                        logger.debug(f"Response Body: {content}")
                except json.JSONDecodeError:
                    # If not JSON, log as text
                    if len(response.text) > 1000:
                        logger.debug(
                            f"Response Body (truncated): {response.text[:1000]}..."
                        )
                    else:
                        logger.debug(f"Response Body: {response.text}")
        except Exception as e:
            logger.warning(f"Failed to log response body: {e}")

    @retry(max_attempts=3, delay=1, backoff=2)
    def request(self, method, endpoint, **kwargs):
        """
        Make an HTTP request with retry mechanism.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters

        Returns:
            requests.Response: Response object

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = self._build_url(endpoint)
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("verify", self.verify_ssl)

        # Update headers
        headers = kwargs.pop("headers", {})
        request_headers = {**self.headers, **headers}
        kwargs["headers"] = request_headers

        # Log request details
        self._log_request(method, url, **kwargs)

        try:
            response = self.session.request(method, url, **kwargs)
            self._log_response(response)
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get(self, endpoint, params=None, **kwargs):
        """
        Make a GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            requests.Response: Response object
        """
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint, data=None, json=None, **kwargs):
        """
        Make a POST request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            **kwargs: Additional request parameters

        Returns:
            requests.Response: Response object
        """
        return self.request("POST", endpoint, data=data, json=json, **kwargs)

    def put(self, endpoint, data=None, json=None, **kwargs):
        """
        Make a PUT request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            **kwargs: Additional request parameters

        Returns:
            requests.Response: Response object
        """
        return self.request("PUT", endpoint, data=data, json=json, **kwargs)

    def delete(self, endpoint, **kwargs):
        """
        Make a DELETE request.

        Args:
            endpoint: API endpoint
            **kwargs: Additional request parameters

        Returns:
            requests.Response: Response object
        """
        return self.request("DELETE", endpoint, **kwargs)

    def patch(self, endpoint, data=None, json=None, **kwargs):
        """
        Make a PATCH request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            **kwargs: Additional request parameters

        Returns:
            requests.Response: Response object
        """
        return self.request("PATCH", endpoint, data=data, json=json, **kwargs)

    def authenticate(self, auth_endpoint, credentials, auth_type="token"):
        """
        Authenticate with the API.

        Args:
            auth_endpoint: Authentication endpoint
            credentials: Authentication credentials
            auth_type: Type of authentication ("token" or "session")

        Returns:
            bool: True if authentication successful

        Raises:
            ValueError: If auth_type is invalid
            requests.exceptions.RequestException: If authentication fails
        """
        if auth_type not in ["token", "session"]:
            raise ValueError('auth_type must be either "token" or "session"')

        try:
            response = self.post(auth_endpoint, json=credentials)

            if auth_type == "token":
                # Extract token from response
                token = response.json().get("token")
                if not token:
                    raise ValueError("No token found in response")

                # Update session headers with token
                self.session.headers["Authorization"] = f"Bearer {token}"
                logger.info("Successfully authenticated with token")

            else:  # session-based auth
                # The session cookie should be automatically handled by requests.Session
                logger.info("Successfully authenticated with session")

            return True

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    @staticmethod
    def validate_status_code(response, expected_codes):
        """
        Validate response status code.

        Args:
            response: Response object
            expected_codes: Expected status code(s)

        Returns:
            bool: True if status code matches expected

        Raises:
            ValueError: If status code doesn't match expected
        """
        if isinstance(expected_codes, int):
            expected_codes = [expected_codes]

        if response.status_code not in expected_codes:
            error_msg = (
                f"Expected status code(s) {expected_codes}, "
                f"got {response.status_code}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        return True

    @staticmethod
    def validate_json_schema(response, schema):
        """
        Validate response against JSON schema.

        Args:
            response: Response object
            schema: JSON schema

        Returns:
            bool: True if validation successful

        Raises:
            ValueError: If validation fails
            json.JSONDecodeError: If response is not valid JSON
        """
        try:
            from jsonschema import ValidationError, validate
        except ImportError:
            error_msg = (
                "JSON schema validation requires jsonschema package. "
                "Install with: pip install jsonschema"
            )
            logger.error(error_msg)
            raise ImportError(error_msg)

        try:
            data = response.json()
            validate(instance=data, schema=schema)
            logger.debug("JSON schema validation successful")
            return True

        except ValidationError as e:
            error_msg = f"JSON schema validation failed: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {e}"
            logger.error(error_msg)
            raise
