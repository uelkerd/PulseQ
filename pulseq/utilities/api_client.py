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

    def __init__(self, base_url, headers=None, timeout=30, verify_ssl=True, max_retries=3):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for all API requests
            headers: Default headers to include in all requests
            timeout: Default request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # Configure retry adapter with more sophisticated retry logic
        retry_adapter = requests.adapters.HTTPAdapter(
            max_retries=max_retries,
            pool_connections=10,
            pool_maxsize=10,
            pool_block=True
        )
        self.session.mount("http://", retry_adapter)
        self.session.mount("https://", retry_adapter)

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

    def _handle_request_exception(self, e, method, url, **kwargs):
        """
        Handle request exceptions with detailed logging and error context.

        Args:
            e: Exception object
            method: HTTP method
            url: Request URL
            **kwargs: Request parameters

        Raises:
            requests.exceptions.RequestException: Enhanced error with context
        """
        error_context = {
            "method": method,
            "url": url,
            "headers": kwargs.get("headers", {}),
            "params": kwargs.get("params"),
            "data": kwargs.get("data"),
            "timeout": kwargs.get("timeout", self.timeout)
        }

        if isinstance(e, requests.exceptions.ConnectionError):
            logger.error(f"Connection error: {str(e)}")
            logger.error(f"Request context: {error_context}")
            raise requests.exceptions.RequestException(
                f"Failed to connect to {url}. Please check your network connection and the server status."
            ) from e

        elif isinstance(e, requests.exceptions.Timeout):
            logger.error(f"Request timeout: {str(e)}")
            logger.error(f"Request context: {error_context}")
            raise requests.exceptions.RequestException(
                f"Request to {url} timed out after {self.timeout} seconds."
            ) from e

        elif isinstance(e, requests.exceptions.HTTPError):
            logger.error(f"HTTP error: {str(e)}")
            logger.error(f"Request context: {error_context}")
            raise requests.exceptions.RequestException(
                f"HTTP error occurred: {str(e)}"
            ) from e

        else:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(f"Request context: {error_context}")
            raise requests.exceptions.RequestException(
                f"An unexpected error occurred: {str(e)}"
            ) from e

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

            # Validate response status code
            if not response.ok:
                error_msg = f"Request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data}"
                except ValueError:
                    error_msg += f": {response.text}"
                logger.error(error_msg)
                response.raise_for_status()

            return response

        except requests.exceptions.RequestException as e:
            self._handle_request_exception(e, method, url, **kwargs)

    @retry(max_attempts=3, delay=1, backoff=2)
    def get(self, endpoint, params=None, headers=None, timeout=None):
        """
        Send a GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout in seconds

        Returns:
            Response object
        """
        url = self._build_url(endpoint)
        headers = headers or {}
        timeout = timeout or self.timeout

        self._log_request("GET", url, params=params, headers=headers)
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                verify=self.verify_ssl
            )
            self._log_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"GET request failed: {e}")
            raise

    @retry(max_attempts=3, delay=1, backoff=2)
    def post(self, endpoint, json=None, data=None, headers=None, timeout=None):
        """
        Send a POST request.

        Args:
            endpoint: API endpoint path
            json: JSON data to send
            data: Form data to send
            headers: Additional headers
            timeout: Request timeout in seconds

        Returns:
            Response object
        """
        url = self._build_url(endpoint)
        headers = headers or {}
        timeout = timeout or self.timeout

        self._log_request("POST", url, json=json, data=data, headers=headers)
        try:
            response = self.session.post(
                url,
                json=json,
                data=data,
                headers=headers,
                timeout=timeout,
                verify=self.verify_ssl
            )
            self._log_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed: {e}")
            raise

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

    def validate_status_code(self, response, expected_code):
        """
        Validate response status code with detailed error message.

        Args:
            response: Response object
            expected_code: Expected status code

        Raises:
            requests.exceptions.HTTPError: If status code doesn't match
        """
        if response.status_code != expected_code:
            error_msg = (
                f"Expected status code {expected_code}, "
                f"but got {response.status_code}"
            )
            try:
                error_data = response.json()
                error_msg += f": {error_data}"
            except ValueError:
                error_msg += f": {response.text}"
            logger.error(error_msg)
            raise requests.exceptions.HTTPError(error_msg)

    def validate_json_schema(self, response, schema):
        """
        Validate response against JSON schema with detailed error messages.

        Args:
            response: Response object
            schema: JSON schema to validate against

        Raises:
            jsonschema.exceptions.ValidationError: If validation fails
        """
        try:
            from jsonschema import validate
            response_data = response.json()
            validate(instance=response_data, schema=schema)
        except ImportError:
            logger.warning("jsonschema package not installed, skipping schema validation")
            raise
        except Exception as e:
            logger.error(f"Schema validation failed: {str(e)}")
            raise
