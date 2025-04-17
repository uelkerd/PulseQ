import json
import os
from pathlib import Path

from jsonschema import ValidationError, validate

from pulseq.utilities.logger import setup_logger

# Set up logger
logger = setup_logger("schema_validator")


class SchemaValidator:
    """
    Utility for validating JSON responses against schemas.
    Supports loading schemas from files or direct dictionary objects.
    """

    def __init__(self, schema_dir="schemas"):
        """
        Initialize the schema validator.

        Args:
            schema_dir: Directory containing schema files
        """
        self.schema_dir = schema_dir
        # Create schema directory if it doesn't exist
        Path(schema_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Initialized SchemaValidator with schema directory: {schema_dir}")

    def load_schema(self, schema_file):
        """
        Load a schema from a file.

        Args:
            schema_file: Name of the schema file in the schema directory

        Returns:
            dict: The loaded schema

        Raises:
            FileNotFoundError: If the schema file doesn't exist
        """
        file_path = os.path.join(self.schema_dir, schema_file)
        try:
            logger.debug(f"Loading schema from {file_path}")
            with open(file_path, "r") as f:
                schema = json.load(f)
            return schema
        except FileNotFoundError:
            logger.error(f"Schema file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file {file_path}: {e}")
            raise

    def save_schema(self, schema, schema_file):
        """
        Save a schema to a file.

        Args:
            schema: Schema dictionary to save
            schema_file: Name of the schema file in the schema directory

        Returns:
            bool: True if successful
        """
        file_path = os.path.join(self.schema_dir, schema_file)
        try:
            logger.debug(f"Saving schema to {file_path}")
            with open(file_path, "w") as f:
                json.dump(schema, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving schema to {file_path}: {e}")
            raise

    def validate_response(self, response_data, schema, schema_name=None):
        """
        Validate a response against a schema.

        Args:
            response_data: Response data to validate (dict or response object with json() method)
            schema: Schema dictionary or filename in schema directory
            schema_name: Optional name to use in log messages

        Returns:
            bool: True if validation passes

        Raises:
            ValidationError: If validation fails
        """
        # Handle response objects
        if hasattr(response_data, "json"):
            try:
                response_data = response_data.json()
            except json.JSONDecodeError as e:
                logger.error(f"Response contains invalid JSON: {e}")
                raise

        # Load schema from file if it's a string
        if isinstance(schema, str):
            schema_file = schema
            schema = self.load_schema(schema_file)
            if not schema_name:
                schema_name = schema_file

        schema_name = schema_name or "provided schema"

        try:
            logger.debug(f"Validating response against {schema_name}")
            validate(instance=response_data, schema=schema)
            logger.info(f"Response validation passed for {schema_name}")
            return True
        except ValidationError as e:
            logger.error(f"Response validation failed for {schema_name}: {e}")
            # Log the problematic data for debugging
            logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
            raise

    def generate_schema_from_response(self, response_data, schema_file=None):
        """
        Generate a basic schema from a response.

        Args:
            response_data: Response data to generate schema from
            schema_file: Optional file to save the generated schema

        Returns:
            dict: The generated schema
        """
        # Handle response objects
        if hasattr(response_data, "json"):
            try:
                response_data = response_data.json()
            except json.JSONDecodeError as e:
                logger.error(f"Response contains invalid JSON: {e}")
                raise

        # Generate basic schema structure based on data types
        schema = self._infer_schema(response_data)

        # Save schema if filename provided
        if schema_file:
            self.save_schema(schema, schema_file)

        return schema

    def _infer_schema(self, data):
        """
        Infer a JSON schema from data.

        Args:
            data: Data to infer schema from

        Returns:
            dict: The inferred schema
        """
        if isinstance(data, dict):
            properties = {}
            for key, value in data.items():
                properties[key] = self._infer_schema(value)
            return {
                "type": "object",
                "properties": properties,
                "required": list(data.keys()),
            }
        elif isinstance(data, list):
            if data:
                # Use the first item as a sample
                return {"type": "array", "items": self._infer_schema(data[0])}
            else:
                return {"type": "array", "items": {}}
        elif isinstance(data, str):
            return {"type": "string"}
        elif isinstance(data, bool):
            return {"type": "boolean"}
        elif isinstance(data, int):
            return {"type": "integer"}
        elif isinstance(data, float):
            return {"type": "number"}
        elif data is None:
            return {"type": "null"}
        else:
            logger.warning(f"Unknown data type for schema inference: {type(data)}")
            return {}
