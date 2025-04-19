# GraphQL Testing Guide

This guide covers the advanced GraphQL testing capabilities of the PulseQ framework.

## Table of Contents

- [Schema Validation](#schema-validation)
- [Query Analysis](#query-analysis)
- [Performance Testing](#performance-testing)
- [Mutation Testing](#mutation-testing)
- [Subscription Testing](#subscription-testing)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Schema Validation

PulseQ provides comprehensive schema validation capabilities:

```typescript
import { GraphQLClient } from "pulseq/utilities/graphql_client";

const client = new GraphQLClient("https://api.example.com/graphql");

// Validate schema
const schema = `
  type User {
    id: ID!
    name: String!
    email: String!
  }
`;

client.validateSchema(schema);
```

### Schema Validation Features

- Type checking
- Field validation
- Directive validation
- Custom scalar validation
- Interface implementation checking

## Query Analysis

Analyze and optimize your GraphQL queries:

```typescript
const query = `
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      name
      posts {
        id
        title
      }
    }
  }
`;

const analysis = client.analyzeQuery(query, {
  complexityLimit: 1000,
  depthLimit: 10,
  costAnalysis: true,
});

console.log("Query Complexity:", analysis.complexity);
console.log("Query Depth:", analysis.depth);
console.log("Estimated Cost:", analysis.cost);
```

### Query Analysis Features

- Complexity calculation
- Depth analysis
- Cost estimation
- Field usage statistics
- Optimization suggestions

## Performance Testing

Measure and analyze GraphQL query performance:

```typescript
const metrics = await client.measurePerformance(query, {
  iterations: 100,
  concurrency: 5,
  warmup: 10,
});

console.log("Average Response Time:", metrics.avgResponseTime);
console.log("P95 Response Time:", metrics.p95ResponseTime);
console.log("Throughput:", metrics.throughput);
```

### Performance Metrics

- Response time distribution
- Memory usage
- CPU utilization
- Network bandwidth
- Cache hit ratio

## Mutation Testing

Test GraphQL mutations with validation:

```typescript
const mutation = `
  mutation CreateUser($input: UserInput!) {
    createUser(input: $input) {
      id
      name
      email
    }
  }
`;

const result = await client.testMutation(mutation, {
  input: {
    name: "John Doe",
    email: "john@example.com",
  },
  validateResponse: true,
  checkPermissions: true,
});
```

### Mutation Testing Features

- Input validation
- Response validation
- Permission checking
- Side effect verification
- Rollback testing

## Subscription Testing

Test GraphQL subscriptions:

```typescript
const subscription = `
  subscription OnUserUpdate {
    userUpdated {
      id
      name
      email
    }
  }
`;

const subscriptionTest = await client.testSubscription(subscription, {
  duration: 5000,
  expectedEvents: 3,
  validatePayload: true,
});

console.log("Received Events:", subscriptionTest.eventCount);
console.log("Latency:", subscriptionTest.avgLatency);
```

### Subscription Testing Features

- Event counting
- Payload validation
- Latency measurement
- Connection stability
- Error handling

## Error Handling

Comprehensive error handling and testing:

```typescript
try {
  await client.executeQuery(query, {
    validateErrors: true,
    expectedErrors: ["UNAUTHENTICATED"],
    retryStrategy: {
      maxAttempts: 3,
      backoff: "exponential",
    },
  });
} catch (error) {
  console.log("Error Type:", error.type);
  console.log("Error Path:", error.path);
  console.log("Error Message:", error.message);
}
```

### Error Testing Features

- Error type validation
- Error path tracking
- Retry strategies
- Error rate monitoring
- Circuit breaker implementation

## Best Practices

1. **Query Optimization**

   - Use fragments for reusable fields
   - Implement query batching
   - Leverage persisted queries
   - Monitor query complexity

2. **Testing Strategy**

   - Test both happy and error paths
   - Validate schema changes
   - Monitor performance metrics
   - Implement automated testing

3. **Security**

   - Validate input thoroughly
   - Implement rate limiting
   - Check permissions
   - Monitor suspicious patterns

4. **Performance**
   - Cache frequently used queries
   - Implement query timeouts
   - Monitor resource usage
   - Optimize database queries

## Example Configuration

```yaml
graphql:
  testing:
    enabled: true
    schemaValidation: true
    queryAnalysis:
      complexityLimit: 1000
      depthLimit: 10
    performance:
      iterations: 100
      concurrency: 5
    errorHandling:
      retryAttempts: 3
      backoffStrategy: exponential
    security:
      rateLimit:
        requests: 100
        period: 60
```

## Troubleshooting

Common issues and solutions:

1. **Schema Validation Failures**

   - Check type definitions
   - Verify field requirements
   - Validate custom scalars

2. **Performance Issues**

   - Analyze query complexity
   - Check database queries
   - Monitor resource usage

3. **Subscription Problems**

   - Verify connection stability
   - Check event delivery
   - Monitor latency

4. **Error Handling**
   - Review error types
   - Check retry logic
   - Validate error responses

## Next Steps

- [API Documentation](../api/README.md)
- [Performance Testing Guide](../features/performance_testing.md)
- [Security Best Practices](../security/README.md)
