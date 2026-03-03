# Architecture

## Overview

```
Client
  │
  ▼
API Gateway (HTTP API)
  │
  ├─ POST   /tickets          → CreateTicketFunction
  ├─ GET    /tickets          → ListTicketsFunction
  ├─ GET    /tickets/{id}     → GetTicketFunction
  ├─ PATCH  /tickets/{id}     → UpdateTicketFunction
  └─ DELETE /tickets/{id}     → DeleteTicketFunction
                                        │
                                        ▼
                                 DynamoDB (Tickets table)
                                        │
                                        ▼
                                 CloudWatch Logs
```

## Components

| Component | Service | Notes |
|---|---|---|
| HTTP API | API Gateway (HTTP API) | Low-latency, cost-effective vs REST API |
| Business logic | AWS Lambda (Python 3.12) | One function per operation |
| Storage | DynamoDB (on-demand) | Single-table, PAY_PER_REQUEST |
| Observability | CloudWatch Logs + X-Ray | Tracing enabled on all Lambdas |
| IAM | Least-privilege SAM policies | `DynamoDBCrudPolicy` / `DynamoDBReadPolicy` |

## DynamoDB Table Design

**Table:** `Tickets`
**Partition key:** `ticketId` (String, UUID)

| Attribute | Type | Values |
|---|---|---|
| ticketId | String | UUID v4 |
| title | String | Free text |
| description | String | Free text |
| status | String | OPEN / IN_PROGRESS / RESOLVED |
| priority | String | LOW / MEDIUM / HIGH |
| channel | String | KIOSK / POS / DMB / DELIVERY |
| createdAt | String | UTC ISO 8601 |
| updatedAt | String | UTC ISO 8601 |

## Lambda Functions

| Function | Method | Path | IAM Policy |
|---|---|---|---|
| CreateTicketFunction | POST | /tickets | DynamoDBCrudPolicy |
| ListTicketsFunction | GET | /tickets | DynamoDBReadPolicy |
| GetTicketFunction | GET | /tickets/{ticketId} | DynamoDBReadPolicy |
| UpdateTicketFunction | PATCH | /tickets/{ticketId} | DynamoDBCrudPolicy |
| DeleteTicketFunction | DELETE | /tickets/{ticketId} | DynamoDBCrudPolicy |

## Shared Code

`src/common/` is a shared layer included in each Lambda package at build time:

- `response.py` — Standard JSON response helpers with CORS headers
- `validate.py` — Field presence checks and enum validation

## Future Improvements

- Add a GSI on `status` or `channel` to replace `scan()` with `query()` for efficiency
- Add request schema validation (JSON Schema / Pydantic)
- Add pagination (`lastEvaluatedKey`) for the list endpoint
- Add structured logging with correlation IDs
- Add a CI/CD pipeline (GitHub Actions → SAM deploy)
