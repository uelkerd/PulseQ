# GraphQL Testing Best Practices

This guide covers best practices and strategies for testing GraphQL APIs using PulseQ.

## Overview

Effective GraphQL testing requires a combination of different testing approaches and strategies. This guide will help you implement comprehensive testing for your GraphQL API.

## Testing Strategy

### 1. Test Coverage Levels

- **Schema Testing**: Validate schema definitions and types
- **Query Testing**: Test individual queries and mutations
- **Integration Testing**: Test interactions between resolvers
- **Performance Testing**: Test query execution time and resource usage
- **Security Testing**: Test authentication, authorization, and vulnerabilities

### 2. Test Organization

```python
from pulseq.graphql import GraphQLClient
import pytest

class TestUserQueries:
    @pytest.fixture
    def client(self):
        return GraphQLClient("https://api.example.com/graphql")

    def test_get_user(self, client):
        response = client.execute_query("""
            query GetUser($id: ID!) {
                user(id: $id) {
                    id
                    name
                    email
                }
            }
        """, variables={"id": "1"})
        assert response.status_code == 200
        assert response.data["user"]["id"] == "1"
```

## Schema Testing

### Type Validation

```python
def test_schema_types():
    schema = client.get_schema()

    # Test type existence
    assert "User" in schema.types
    assert "Post" in schema.types

    # Test field types
    user_type = schema.types["User"]
    assert user_type.fields["id"].type == "ID"
    assert user_type.fields["name"].type == "String"
```

### Input Validation

```python
def test_input_validation():
    # Test required fields
    response = client.execute_query("""
        mutation CreateUser($input: CreateUserInput!) {
            createUser(input: $input) {
                id
            }
        }
    """, variables={"input": {"name": "John"}})
    assert response.status_code == 400  # email is required
```

## Query Testing

### Basic Query Testing

```python
def test_basic_query():
    response = client.execute_query("""
        query {
            users {
                id
                name
            }
        }
    """)
    assert response.status_code == 200
    assert isinstance(response.data["users"], list)
```

### Nested Query Testing

```python
def test_nested_query():
    response = client.execute_query("""
        query {
            users {
                id
                posts {
                    id
                    title
                    comments {
                        id
                        text
                    }
                }
            }
        }
    """)
    assert response.status_code == 200
    assert all("posts" in user for user in response.data["users"])
```

## Mutation Testing

### Create Operations

```python
def test_create_mutation():
    response = client.execute_query("""
        mutation CreatePost($input: CreatePostInput!) {
            createPost(input: $input) {
                id
                title
                content
            }
        }
    """, variables={
        "input": {
            "title": "Test Post",
            "content": "Test Content"
        }
    })
    assert response.status_code == 200
    assert response.data["createPost"]["title"] == "Test Post"
```

### Update Operations

```python
def test_update_mutation():
    response = client.execute_query("""
        mutation UpdatePost($id: ID!, $input: UpdatePostInput!) {
            updatePost(id: $id, input: $input) {
                id
                title
                content
            }
        }
    """, variables={
        "id": "1",
        "input": {
            "title": "Updated Title"
        }
    })
    assert response.status_code == 200
    assert response.data["updatePost"]["title"] == "Updated Title"
```

## Error Handling

### Expected Errors

```python
def test_error_handling():
    response = client.execute_query("""
        query {
            nonExistentField
        }
    """)
    assert response.status_code == 400
    assert "errors" in response.data
```

### Custom Error Messages

```python
def test_custom_errors():
    response = client.execute_query("""
        mutation {
            createPost(input: {}) {
                id
            }
        }
    """)
    assert response.status_code == 400
    assert "validation" in response.data["errors"][0]["message"].lower()
```

## Testing Best Practices

1. **Test Organization**

   - Group tests by feature or domain
   - Use descriptive test names
   - Maintain test isolation

2. **Query Design**

   - Test both simple and complex queries
   - Include error cases
   - Test with different variables

3. **Mutation Testing**

   - Test all CRUD operations
   - Validate input constraints
   - Check side effects

4. **Error Handling**

   - Test expected errors
   - Validate error messages
   - Check error codes

5. **Performance Considerations**
   - Monitor query complexity
   - Test with realistic data volumes
   - Consider caching strategies

## Testing Checklist

1. **Schema Validation**

   - [ ] Test type definitions
   - [ ] Validate field types
   - [ ] Check required fields

2. **Query Testing**

   - [ ] Test basic queries
   - [ ] Test nested queries
   - [ ] Test with variables

3. **Mutation Testing**

   - [ ] Test create operations
   - [ ] Test update operations
   - [ ] Test delete operations

4. **Error Handling**

   - [ ] Test validation errors
   - [ ] Test authorization errors
   - [ ] Test custom errors

5. **Integration Testing**
   - [ ] Test resolver interactions
   - [ ] Test data consistency
   - [ ] Test edge cases

## Conclusion

Following these best practices will help you create comprehensive and effective tests for your GraphQL API. Remember to regularly review and update your tests as your API evolves.
