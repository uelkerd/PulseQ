# tests/api/test_api_documentation.py
import pytest
import json
import os
from pathlib import Path

from pulseq.utilities.api_client import APIClient
from pulseq.utilities.schema_validator import SchemaValidator
from pulseq.utilities.logger import setup_logger

# Set up logger
logger = setup_logger("api_documentation")

# Base URL for ReqRes API
BASE_URL = "https://reqres.in/api"

# API endpoints to document
ENDPOINTS = [
    {"method": "GET", "path": "/users", "params": {"page": 1}, "description": "List users"},
    {"method": "GET", "path": "/users/2", "description": "Get single user"},
    {"method": "POST", "path": "/users", "json": {"name": "morpheus", "job": "leader"}, "description": "Create user"},
    {"method": "PUT", "path": "/users/2", "json": {"name": "morpheus", "job": "zion resident"}, "description": "Update user"},
    {"method": "DELETE", "path": "/users/2", "description": "Delete user"},
    {"method": "POST", "path": "/register", "json": {"email": "eve.holt@reqres.in", "password": "pistol"}, "description": "Register user"},
    {"method": "POST", "path": "/login", "json": {"email": "eve.holt@reqres.in", "password": "cityslicka"}, "description": "Login user"},
]

@pytest.fixture
def api_client():
    """Initialize the API client."""
    client = APIClient(BASE_URL)
    return client

@pytest.fixture
def schema_validator():
    """Initialize the schema validator."""
    # Create schemas directory in docs folder
    schema_dir = "docs/schemas"
    Path(schema_dir).mkdir(parents=True, exist_ok=True)
    return SchemaValidator(schema_dir=schema_dir)

def test_generate_api_documentation(api_client, schema_validator):
    """
    Generate API documentation by calling endpoints and documenting responses.
    """
    # Create directory for API documentation
    docs_dir = "docs/api"
    Path(docs_dir).mkdir(parents=True, exist_ok=True)
    
    # Initialize the documentation
    docs = {
        "baseUrl": BASE_URL,
        "endpoints": []
    }
    
    # Process each endpoint
    for endpoint in ENDPOINTS:
        method = endpoint["method"]
        path = endpoint["path"]
        description = endpoint.get("description", "")
        
        logger.info(f"Documenting {method} {path}")
        
        # Prepare request parameters
        kwargs = {}
        for param in ["params", "json", "data", "headers"]:
            if param in endpoint:
                kwargs[param] = endpoint[param]
        
        try:
            # Make the request
            if method == "GET":
                response = api_client.get(path, **kwargs)
            elif method == "POST":
                response = api_client.post(path, **kwargs)
            elif method == "PUT":
                response = api_client.put(path, **kwargs)
            elif method == "DELETE":
                response = api_client.delete(path, **kwargs)
            elif method == "PATCH":
                response = api_client.patch(path, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Document request and response
            endpoint_doc = {
                "method": method,
                "path": path,
                "description": description,
                "request": {
                    **kwargs
                },
                "response": {
                    "status": response.status_code,
                    "headers": dict(response.headers),
                }
            }
            
            # Add response body for non-DELETE methods
            if method != "DELETE":
                try:
                    endpoint_doc["response"]["body"] = response.json()
                    
                    # Generate schema if response is successful
                    if 200 <= response.status_code < 300:
                        schema_file = f"{method.lower()}{path.replace('/', '_')}.json"
                        schema = schema_validator.generate_schema_from_response(
                            response, schema_file)
                        endpoint_doc["response"]["schema"] = schema_file
                except:
                    endpoint_doc["response"]["body"] = response.text
            
            docs["endpoints"].append(endpoint_doc)
            
        except Exception as e:
            logger.error(f"Error documenting {method} {path}: {e}")
            # Add error to documentation
            docs["endpoints"].append({
                "method": method,
                "path": path,
                "description": description,
                "error": str(e)
            })
    
    # Save the documentation
    docs_file = os.path.join(docs_dir, "api_documentation.json")
    with open(docs_file, 'w') as f:
        json.dump(docs, f, indent=2)
    
    # Generate Markdown documentation
    md_file = os.path.join(docs_dir, "api_documentation.md")
    with open(md_file, 'w') as f:
        f.write("# API Documentation\n\n")
        f.write(f"Base URL: {docs['baseUrl']}\n\n")
        
        for endpoint in docs["endpoints"]:
            f.write(f"## {endpoint['method']} {endpoint['path']}\n\n")
            f.write(f"{endpoint.get('description', '')}\n\n")
            
            if "request" in endpoint:
                f.write("### Request\n\n")
                if "params" in endpoint["request"]:
                    f.write("**Query Parameters:**\n\n")
                    f.write("```json\n")
                    f.write(json.dumps(endpoint["request"]["params"], indent=2))
                    f.write("\n```\n\n")
                
                if "json" in endpoint["request"]:
                    f.write("**Request Body:**\n\n")
                    f.write("```json\n")
                    f.write(json.dumps(endpoint["request"]["json"], indent=2))
                    f.write("\n```\n\n")
            
            if "response" in endpoint:
                f.write("### Response\n\n")
                f.write(f"**Status:** {endpoint['response']['status']}\n\n")
                
                if "body" in endpoint["response"]:
                    f.write("**Response Body:**\n\n")
                    if isinstance(endpoint["response"]["body"], (dict, list)):
                        f.write("```json\n")
                        f.write(json.dumps(endpoint["response"]["body"], indent=2))
                        f.write("\n```\n\n")
                    else:
                        f.write("```\n")
                        f.write(endpoint["response"]["body"])
                        f.write("\n```\n\n")
                
                if "schema" in endpoint["response"]:
                    f.write(f"**Schema:** [View Schema](../schemas/{endpoint['response']['schema']})\n\n")
            
            if "error" in endpoint:
                f.write("### Error\n\n")
                f.write(f"```\n{endpoint['error']}\n```\n\n")
    
    logger.info(f"API documentation generated: {md_file}")
    assert os.path.exists(md_file), "API documentation file was not created" 