# Serverless Ticket Tracker

A production-style REST API for managing support tickets across digital ordering channels — built with **AWS Lambda (Python 3.12)**, **DynamoDB**, and **API Gateway HTTP API**, deployed via **AWS SAM**.

---

## Architecture

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
                                 CloudWatch Logs + X-Ray
```

See [docs/architecture.md](docs/architecture.md) for full component breakdown.

---

## Data Model (DynamoDB)

**Table:** `Tickets` | **PK:** `ticketId` (String, UUID)

| Attribute | Type | Values |
|---|---|---|
| ticketId | String | UUID v4 |
| title | String | Free text |
| description | String | Free text |
| status | String | `OPEN` / `IN_PROGRESS` / `RESOLVED` |
| priority | String | `LOW` / `MEDIUM` / `HIGH` |
| channel | String | `KIOSK` / `POS` / `DMB` / `DELIVERY` |
| createdAt | String | UTC ISO 8601 |
| updatedAt | String | UTC ISO 8601 |

---

## API Endpoints

### POST /tickets — Create ticket

**Request body:**
```json
{
  "title": "POS menu not updating",
  "description": "Store 142 menu item missing",
  "priority": "HIGH",
  "channel": "POS"
}
```

**Response `201`:**
```json
{
  "ticketId": "uuid",
  "title": "POS menu not updating",
  "description": "Store 142 menu item missing",
  "status": "OPEN",
  "priority": "HIGH",
  "channel": "POS",
  "createdAt": "2026-03-02T12:00:00+00:00",
  "updatedAt": "2026-03-02T12:00:00+00:00"
}
```

### GET /tickets — List tickets

Optional query params: `status`, `channel`

```
GET /tickets
GET /tickets?status=OPEN
GET /tickets?channel=DELIVERY
GET /tickets?status=IN_PROGRESS&channel=POS
```

**Response `200`:**
```json
{ "count": 2, "items": [...] }
```

### GET /tickets/{ticketId} — Get ticket

**Response `200`:** Full ticket object
**Response `404`:** `{ "error": "Ticket not found" }`

### PATCH /tickets/{ticketId} — Update ticket

Updatable fields: `title`, `description`, `status`, `priority`, `channel`

```json
{ "status": "IN_PROGRESS" }
```

**Response `200`:** Updated ticket object
**Response `404`:** `{ "error": "Ticket not found" }`

### DELETE /tickets/{ticketId} — Delete ticket

**Response `200`:** `{ "deleted": true, "ticketId": "uuid" }`
**Response `404`:** `{ "error": "Ticket not found" }`

---

## Deploy (AWS SAM)

### Prerequisites

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) configured (`aws configure`)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) installed

### Build and deploy

```bash
# 1. Sync the shared common/ module into each Lambda package
chmod +x scripts/sync_common.sh
./scripts/sync_common.sh

# 2. Build and deploy
cd infra
sam build
sam deploy --guided
```

On first deploy, SAM will prompt for:
- Stack name (e.g. `serverless-ticket-tracker`)
- AWS Region (e.g. `us-east-1`)
- Confirm IAM role creation: **Y**
- Save settings to `samconfig.toml`: **Y**

After deploy, copy the `ApiBaseUrl` from the Outputs section.

### Subsequent deploys

```bash
./scripts/sync_common.sh && cd infra && sam build && sam deploy
```

---

## Testing (curl)

Set your base URL:

```bash
export BASE_URL="https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod"
```

**Create a ticket:**
```bash
curl -s -X POST "$BASE_URL/tickets" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "POS menu not updating",
    "description": "Store 142 menu item missing",
    "priority": "HIGH",
    "channel": "POS"
  }' | jq .
```

**List all tickets:**
```bash
curl -s "$BASE_URL/tickets" | jq .
```

**List by status:**
```bash
curl -s "$BASE_URL/tickets?status=OPEN" | jq .
```

**Get one ticket:**
```bash
curl -s "$BASE_URL/tickets/TICKET_ID_HERE" | jq .
```

**Update status to IN_PROGRESS:**
```bash
curl -s -X PATCH "$BASE_URL/tickets/TICKET_ID_HERE" \
  -H "Content-Type: application/json" \
  -d '{"status": "IN_PROGRESS"}' | jq .
```

**Resolve a ticket:**
```bash
curl -s -X PATCH "$BASE_URL/tickets/TICKET_ID_HERE" \
  -H "Content-Type: application/json" \
  -d '{"status": "RESOLVED"}' | jq .
```

**Delete a ticket:**
```bash
curl -s -X DELETE "$BASE_URL/tickets/TICKET_ID_HERE" | jq .
```

---

## Monitoring & Troubleshooting

- **Logs:** Each Lambda writes structured logs to CloudWatch under `/aws/lambda/<FunctionName>`
- **Tracing:** X-Ray active tracing enabled on all functions
- **Errors:** Non-2xx responses include an `error` field and optional `details` with the DynamoDB error code

```bash
# Tail logs for CreateTicketFunction
sam logs -n CreateTicketFunction --stack-name serverless-ticket-tracker --tail
```

---

## Project Structure

```
serverless-ticket-tracker/
  infra/
    template.yaml         # SAM template (DynamoDB + 5 Lambdas + HTTP API)
  src/
    common/
      response.py         # JSON response helpers with CORS headers
      validate.py         # Field validation + enum checks
    create_ticket/
      app.py
      requirements.txt
    get_ticket/
      app.py
      requirements.txt
    list_tickets/
      app.py
      requirements.txt
    update_ticket/
      app.py
      requirements.txt
    delete_ticket/
      app.py
      requirements.txt
  docs/
    architecture.md
  .gitignore
  README.md
```

---

## Improvements / Roadmap

- [ ] Add GSI on `status` or `channel` to replace `scan()` with `query()` for scale
- [ ] Pagination (`lastEvaluatedKey`) on the list endpoint
- [ ] JSON Schema request validation
- [ ] Structured logging with correlation IDs
- [ ] GitHub Actions CI/CD pipeline → `sam deploy`
- [ ] Unit tests with `pytest` + `moto` (DynamoDB mock)

---

## Resume Bullets

- Built a serverless REST API using AWS Lambda (Python), API Gateway, and DynamoDB to manage production-style support tickets across multiple digital ordering channels (KIOSK, POS, DMB, DELIVERY).
- Implemented full CRUD workflows with conditional writes for idempotent updates, DynamoDB 404 handling, and CORS support for frontend integration.
- Packaged infrastructure as code with AWS SAM and documented repeatable deployment and API testing procedures in GitHub.
- Enabled observability with CloudWatch structured logging and X-Ray active tracing across all Lambda functions.

---

## Initialize GitHub Repo

```bash
git init
git add .
git commit -m "Initial serverless ticket tracker (Lambda + DynamoDB + SAM)"
git branch -M main
git remote add origin https://github.com/YOUR_USER/serverless-ticket-tracker.git
git push -u origin main
```
