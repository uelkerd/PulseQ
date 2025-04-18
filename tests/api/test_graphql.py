import pytest
import os
from pulseq.utilities.graphql_client import GraphQLClient
from datetime import datetime

@pytest.fixture
async def github_client():
    """Fixture for GitHub GraphQL API client."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        pytest.skip("GITHUB_TOKEN environment variable not set")
    
    client = GraphQLClient(
        endpoint='https://api.github.com/graphql',
        headers={'Authorization': f'Bearer {token}'}
    )
    yield client
    client.close()

@pytest.mark.asyncio
async def test_repository_info(github_client):
    """Test querying repository information."""
    query = """
    query ($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            name
            description
            createdAt
            stargazerCount
            primaryLanguage {
                name
            }
        }
    }
    """
    
    variables = {
        "owner": "uelkerd",
        "name": "PulseQ"
    }
    
    result = await github_client.execute_query(query, variables)
    
    assert result['repository']['name'] == "PulseQ"
    assert 'description' in result['repository']
    assert isinstance(result['repository']['stargazerCount'], int)
    
    # Verify created date format
    created_at = result['repository']['createdAt']
    datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")

@pytest.mark.asyncio
async def test_repository_issues(github_client):
    """Test querying repository issues."""
    query = """
    query ($owner: String!, $name: String!, $states: [IssueState!]) {
        repository(owner: $owner, name: $name) {
            issues(first: 10, states: $states) {
                nodes {
                    title
                    state
                    createdAt
                    author {
                        login
                    }
                }
            }
        }
    }
    """
    
    variables = {
        "owner": "uelkerd",
        "name": "PulseQ",
        "states": ["OPEN"]
    }
    
    result = await github_client.execute_query(query, variables)
    
    issues = result['repository']['issues']['nodes']
    for issue in issues:
        assert issue['state'] == 'OPEN'
        assert 'title' in issue
        assert 'author' in issue
        # Verify date format
        datetime.strptime(issue['createdAt'], "%Y-%m-%dT%H:%M:%SZ")

@pytest.mark.asyncio
async def test_schema_introspection(github_client):
    """Test schema introspection capabilities."""
    schema = await github_client.introspect_schema()
    
    # Verify schema structure
    assert '__schema' in schema
    assert 'types' in schema['__schema']
    
    # Get fields for Repository type
    repo_fields = await github_client.get_type_fields('Repository')
    
    # Verify common repository fields exist
    assert 'name' in repo_fields
    assert 'description' in repo_fields
    assert 'createdAt' in repo_fields

@pytest.mark.asyncio
async def test_mutation(github_client):
    """Test a mutation operation (adding a star)."""
    mutation = """
    mutation ($repositoryId: ID!) {
        addStar(input: {starrableId: $repositoryId}) {
            starrable {
                stargazerCount
            }
        }
    }
    """
    
    # First get the repository ID
    id_query = """
    query ($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            id
        }
    }
    """
    
    variables = {
        "owner": "uelkerd",
        "name": "PulseQ"
    }
    
    # Get repository ID
    result = await github_client.execute_query(id_query, variables)
    repo_id = result['repository']['id']
    
    # Execute mutation
    try:
        result = await github_client.execute_mutation(mutation, {"repositoryId": repo_id})
        assert 'addStar' in result
        assert 'starrable' in result['addStar']
        assert isinstance(result['addStar']['starrable']['stargazerCount'], int)
    except Exception as e:
        # The mutation might fail if already starred - that's OK
        assert "already starred" in str(e).lower()

@pytest.mark.asyncio
async def test_query_validation(github_client):
    """Test query validation functionality."""
    # Valid query
    valid_query = """
    query {
        viewer {
            login
        }
    }
    """
    assert github_client.validate_query(valid_query) is True
    
    # Invalid query
    invalid_query = """
    query {
        invalid {
            field
    }
    """
    assert github_client.validate_query(invalid_query) is False 