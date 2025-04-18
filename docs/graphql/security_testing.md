# GraphQL Security Testing

This guide covers security testing strategies and best practices for GraphQL APIs using PulseQ.

## Overview

Security testing is critical for ensuring your GraphQL API is protected against common vulnerabilities and attacks. PulseQ provides tools and features to help you test and secure your GraphQL API.

## Common GraphQL Security Risks

1. **Introspection Exploitation**

   - Unauthorized schema access
   - Information disclosure
   - Attack surface exposure

2. **Query Complexity Attacks**

   - Denial of Service (DoS)
   - Resource exhaustion
   - N+1 query problems

3. **Authentication & Authorization**

   - Broken access control
   - Missing authentication
   - Insecure direct object references

4. **Data Exposure**
   - Sensitive data leakage
   - Over-fetching
   - Insecure error messages

## Security Testing Features

### Introspection Control Testing

```python
from pulseq.graphql import GraphQLClient

client = GraphQLClient("https://api.example.com/graphql")

def test_introspection_control():
    # Test if introspection is disabled in production
    response = client.execute_query("""
        query {
            __schema {
                types {
                    name
                }
            }
        }
    """)
    assert response.status_code == 403, "Introspection should be disabled"
```

### Query Complexity Protection

```python
def test_query_complexity_protection():
    # Test protection against complex queries
    complex_query = """
        query {
            users {
                id
                posts {
                    id
                    comments {
                        id
                        author {
                            id
                            posts {
                                id
                                comments {
                                    id
                                }
                            }
                        }
                    }
                }
            }
        }
    """
    response = client.execute_query(complex_query)
    assert response.status_code == 400, "Complex queries should be rejected"
```

### Authentication Testing

```python
def test_authentication():
    # Test authentication requirements
    response = client.execute_query("""
        query {
            users {
                id
                email
            }
        }
    """)
    assert response.status_code == 401, "Authentication should be required"
```

## Security Testing Scenarios

### Basic Security Tests

```python
def test_basic_security():
    # Test for common security headers
    response = client.execute_query("""
        query {
            __typename
        }
    """)
    headers = response.headers

    assert "X-Content-Type-Options" in headers
    assert "X-Frame-Options" in headers
    assert "X-XSS-Protection" in headers
```

### Authorization Testing

```python
def test_authorization():
    # Test role-based access control
    admin_query = """
        query {
            adminSettings {
                id
                value
            }
        }
    """

    # Test as regular user
    response = client.execute_query(admin_query)
    assert response.status_code == 403, "Regular users should not access admin settings"

    # Test as admin
    admin_client = GraphQLClient(
        "https://api.example.com/graphql",
        headers={"Authorization": "Bearer admin-token"}
    )
    response = admin_client.execute_query(admin_query)
    assert response.status_code == 200, "Admins should access admin settings"
```

### Input Validation Testing

```python
def test_input_validation():
    # Test for SQL injection prevention
    malicious_query = """
        query {
            users(filter: "1=1; DROP TABLE users;") {
                id
            }
        }
    """
    response = client.execute_query(malicious_query)
    assert response.status_code == 400, "Malicious input should be rejected"
```

## Security Best Practices

1. **Authentication & Authorization**

   - Implement proper authentication
   - Use role-based access control
   - Validate permissions at resolver level

2. **Query Complexity**

   - Set query depth limits
   - Implement cost analysis
   - Use query whitelisting

3. **Data Protection**

   - Implement field-level authorization
   - Sanitize error messages
   - Use data masking where appropriate

4. **Monitoring & Logging**
   - Log security events
   - Monitor for suspicious queries
   - Set up security alerts

## Security Testing Checklist

1. **Authentication**

   - [ ] Test unauthenticated access
   - [ ] Test token validation
   - [ ] Test session management

2. **Authorization**

   - [ ] Test role-based access
   - [ ] Test resource ownership
   - [ ] Test permission boundaries

3. **Input Validation**

   - [ ] Test query injection
   - [ ] Test input sanitization
   - [ ] Test type coercion

4. **Error Handling**
   - [ ] Test error message exposure
   - [ ] Test stack trace leakage
   - [ ] Test graceful failure

## Conclusion

Regular security testing is essential for maintaining a secure GraphQL API. By following these guidelines and using PulseQ's security testing features, you can identify and mitigate potential security vulnerabilities in your API.
