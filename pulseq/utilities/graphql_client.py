from typing import Any, Dict, Optional, Union
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
import asyncio
import logging
from datetime import datetime

class GraphQLClient:
    """A GraphQL client for making queries and mutations."""
    
    def __init__(self, endpoint: str, headers: Optional[Dict[str, str]] = None):
        """Initialize the GraphQL client.
        
        Args:
            endpoint: The GraphQL endpoint URL
            headers: Optional headers for authentication etc.
        """
        self.endpoint = endpoint
        self.headers = headers or {}
        self.logger = logging.getLogger(__name__)
        self._setup_transport()
        
    def _setup_transport(self):
        """Set up the GraphQL transport with the configured endpoint and headers."""
        self.transport = AIOHTTPTransport(
            url=self.endpoint,
            headers=self.headers
        )
        self.client = Client(
            transport=self.transport,
            fetch_schema_from_transport=True
        )
        
    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query.
        
        Args:
            query: The GraphQL query string
            variables: Optional variables for the query
            
        Returns:
            The query response data
            
        Raises:
            TransportQueryError: If the query fails
        """
        try:
            start_time = datetime.now()
            async with self.client as session:
                result = await session.execute(
                    gql(query),
                    variable_values=variables
                )
            execution_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"GraphQL query executed in {execution_time:.2f} seconds")
            self.logger.debug(f"Query: {query}")
            self.logger.debug(f"Variables: {variables}")
            self.logger.debug(f"Result: {result}")
            
            return result
        except TransportQueryError as e:
            self.logger.error(f"GraphQL query failed: {str(e)}")
            self.logger.debug(f"Query: {query}")
            self.logger.debug(f"Variables: {variables}")
            raise
            
    async def execute_mutation(self, mutation: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL mutation.
        
        Args:
            mutation: The GraphQL mutation string
            variables: Optional variables for the mutation
            
        Returns:
            The mutation response data
            
        Raises:
            TransportQueryError: If the mutation fails
        """
        return await self.execute_query(mutation, variables)
    
    def validate_query(self, query: str) -> bool:
        """Validate a GraphQL query against the schema.
        
        Args:
            query: The GraphQL query string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Parse the query to validate it
            gql(query)
            return True
        except Exception as e:
            self.logger.error(f"Invalid GraphQL query: {str(e)}")
            return False
            
    async def introspect_schema(self) -> Dict[str, Any]:
        """Perform schema introspection.
        
        Returns:
            The schema introspection data
        """
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    description
                    fields {
                        name
                        description
                        type {
                            name
                        }
                    }
                }
            }
        }
        """
        return await self.execute_query(introspection_query)
    
    async def get_type_fields(self, type_name: str) -> list:
        """Get fields for a specific type.
        
        Args:
            type_name: Name of the type to get fields for
            
        Returns:
            List of field names for the type
        """
        schema = await self.introspect_schema()
        for type_def in schema['__schema']['types']:
            if type_def['name'] == type_name:
                return [field['name'] for field in type_def.get('fields', [])]
        return []
    
    def close(self):
        """Close the client and clean up resources."""
        if hasattr(self, 'transport'):
            asyncio.create_task(self.transport.close()) 