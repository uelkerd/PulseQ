# framework/utilities/api_client.py

import requests
import json
import logging
import time
from framework.utilities.logger import setup_logger
from framework.utilities.retry import retry

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
        self.base_url = base_url.rstrip('/')
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
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _log_request(self, method, url, **kwargs):
        """
        Log request details.
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Request parameters
        """
        headers = kwargs.get('headers', {})
        # Sanitize headers to avoid logging sensitive information
        sanitized_headers = {}
        for key, value in headers.items():
            if key.lower() in ['authorization', 'api-key', 'token']:
                sanitized_headers[key] = '********'
            else:
                sanitized_headers[key] = value
                
        data = kwargs.get('data')
        if data and isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass
                
        params = kwargs.get('params')
        
        logger.debug(f"API Request: {method} {url}")
        logger.debug(f"Headers: {sanitized_headers}")
        
        if params:
            logger.debug(f"Query Parameters: {params}")
        
        if data:
            logger.debug(f"Request Body: {data}")
    
    def _log_response(self, response):
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
                        logger.debug(f"Response Body (truncated): {content_str[:1000]}...")
                    else:
                        logger.debug(f"Response Body: {content}")
                except json.JSONDecodeError:
                    # Otherwise log as text
                    if len(response.text) > 1000:
                        logger.debug(f"Response Text (truncated): {response.text[:1000]}...")
                    else:
                        logger.debug(f"Response Text: {response.text}")
        except Exception as e:
            logger.error(f"Error logging response: {e}")
    
    @retry(max_attempts=3, delay=1, backoff=2)
    def request(self, method, endpoint, **kwargs):
        """
        Make an HTTP request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Response: Response object
            
        Raises:
            requests.RequestException: If the request fails
        """
        url = self._build_url(endpoint)
        
        # Set default timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
            
        # Set default verify_ssl if not provided
        if 'verify' not in kwargs:
            kwargs['verify'] = self.verify_ssl
            
        # Merge default headers with request-specific headers
        headers = kwargs.get('headers', {})
        all_headers = {**self.session.headers, **headers}
        kwargs['headers'] = all_headers
        
        # Log request details
        self._log_request(method, url, **kwargs)
        
        # Record request time
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Log response details
            elapsed_time = time.time() - start_time
            logger.debug(f"Request completed in {elapsed_time:.2f} seconds")
            self._log_response(response)
            
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def get(self, endpoint, params=None, **kwargs):
        """
        Make a GET request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional request parameters
            
        Returns:
            Response: Response object
        """
        return self.request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint, data=None, json=None, **kwargs):
        """
        Make a POST request.
        
        Args:
            endpoint: API endpoint path
            data: Form data or raw data
            json: JSON data (will be converted to string)
            **kwargs: Additional request parameters
            
        Returns:
            Response: Response object
        """
        return self.request('POST', endpoint, data=data, json=json, **kwargs)
    
    def put(self, endpoint, data=None, json=None, **kwargs):
        """
        Make a PUT request.
        
        Args:
            endpoint: API endpoint path
            data: Form data or raw data
            json: JSON data (will be converted to string)
            **kwargs: Additional request parameters
            
        Returns:
            Response: Response object
        """
        return self.request('PUT', endpoint, data=data, json=json, **kwargs)
    
    def delete(self, endpoint, **kwargs):
        """
        Make a DELETE request.
        
        Args:
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Response: Response object
        """
        return self.request('DELETE', endpoint, **kwargs)
    
    def patch(self, endpoint, data=None, json=None, **kwargs):
        """
        Make a PATCH request.
        
        Args:
            endpoint: API endpoint path
            data: Form data or raw data
            json: JSON data (will be converted to string)
            **kwargs: Additional request parameters
            
        Returns:
            Response: Response object
        """
        return self.request('PATCH', endpoint, data=data, json=json, **kwargs)
    
    def authenticate(self, auth_endpoint, credentials, auth_type="token"):
        """
        Authenticate with the API and store authentication token.
        
        Args:
            auth_endpoint: Authentication endpoint
            credentials: Authentication credentials (dict)
            auth_type: Type of authentication ('token', 'jwt', 'oauth')
            
        Returns:
            bool: True if authentication successful
            
        Raises:
            ValueError: If authentication fails
        """
        logger.debug(f"Authenticating with {auth_type} authentication")
        
        try:
            response = self.post(auth_endpoint, json=credentials)
            
            if response.status_code not in (200, 201):
                error_msg = f"Authentication failed with status code {response.status_code}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            auth_data = response.json()
            
            # Extract token based on auth type
            token = None
            
            if auth_type == "token":
                token = auth_data.get('token') or auth_data.get('access_token')
            elif auth_type == "jwt":
                token = auth_data.get('jwt') or auth_data.get('token')
            elif auth_type == "oauth":
                token = auth_data.get('access_token')
            
            if not token:
                error_msg = f"Authentication response did not contain expected token for {auth_type} auth"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Add token to default headers
            self.session.headers.update({
                'Authorization': f"Bearer {token}"
            })
            
            logger.debug("Authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise
    
    def validate_status_code(self, response, expected_codes):
        """
        Validate response status code.
        
        Args:
            response: Response object
            expected_codes: Expected status code(s) as int or list/tuple
            
        Returns:
            bool: True if status code matches expected
            
        Raises:
            AssertionError: If status code doesn't match expected
        """
        if isinstance(expected_codes, (list, tuple)):
            is_valid = response.status_code in expected_codes
            expected_str = f"one of {expected_codes}"
        else:
            is_valid = response.status_code == expected_codes
            expected_str = str(expected_codes)
            
        if not is_valid:
            error_msg = f"Expected status code {expected_str}, got {response.status_code}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
            
        return True
    
    def validate_json_schema(self, response, schema):
        """
        Validate response against a JSON schema.
        
        Args:
            response: Response object
            schema: JSON schema dictionary
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If response is not JSON
            ImportError: If jsonschema package is not installed
            jsonschema.exceptions.ValidationError: If validation fails
        """
        try:
            # Import here to make this dependency optional
            from jsonschema import validate, ValidationError
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                error_msg = "Response is not valid JSON"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            try:
                validate(instance=data, schema=schema)
                logger.debug("JSON schema validation passed")
                return True
            except ValidationError as e:
                error_msg = f"JSON schema validation failed: {e}"
                logger.error(error_msg)
                raise
                
        except ImportError:
            error_msg = "jsonschema package is required for schema validation. Install with pip install jsonschema"
            logger.error(error_msg)
            raise ImportError(error_msg)

# Example usage
if __name__ == "__main__":
    # Create an API client
    api = APIClient(base_url="https://reqres.in/api")
    
    # Make a GET request
    response = api.get("users", params={"page": 1})
    print(f"Status Code: {response.status_code}")
    print(f"Response JSON: {response.json()}")
    
    # Validate status code
    api.validate_status_code(response, 200)