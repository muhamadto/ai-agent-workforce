---
name: api-design
description: Design and review REST/OpenAPI 3.1 and gRPC/proto3 API contracts for correctness, completeness, security, and business alignment.
---

# API Design & Review Skill

Use this skill when designing a new API contract or reviewing an existing one before implementation or merge.

---

## Part 1 — Design

### URI

```
METHOD /api/v{n}/resource/{id}/sub-resource
```

- Lowercase, hyphen-separated path segments
- Version in the URL prefix (`/api/v1/`)
- Path parameters in `{camelCase}`

### Request

| Element | Required | Notes |
|---------|----------|-------|
| Method | yes | GET · POST · PUT · PATCH · DELETE |
| `Authorization` header | yes (non-public) | `Bearer <token>` |
| `Content-Type` header | yes (body) | `application/json` |
| `Idempotency-Key` header | when POST creates a resource | UUID v4, client-generated |
| Path parameters | when present | name, type, constraints |
| Query parameters | when present | name, type, default, max |
| Request body schema | POST · PUT · PATCH | all fields with types, required/optional, constraints |

### Response

| Method | Success code | Required response headers | Body |
|--------|-------------|--------------------------|------|
| `POST` | **201 Created** | `Location: /api/v1/resource/{newId}` | created resource |
| `PUT` | **200 OK** | — | updated resource |
| `PATCH` | **200 OK** | — | updated resource |
| `GET` (single) | **200 OK** | — | resource |
| `GET` (list) | **200 OK** | — | `{ data: [], meta: { total, limit, offset, hasMore } }` |
| `DELETE` | **204 No Content** | — | empty |

All responses use a consistent envelope:

```json
{
  "success": true,
  "data": { },
  "error": null,
  "meta": null
}
```

### Error Codes

| Code | Meaning | When to return |
|------|---------|----------------|
| `400` Bad Request | Malformed request syntax | Unparseable JSON, wrong content type |
| `401` Unauthorized | Missing or invalid credentials | No token, expired token, bad signature |
| `403` Forbidden | Authenticated but not permitted | Valid token, wrong scope or role |
| `404` Not Found | Resource does not exist | ID not in the data store |
| `409` Conflict | State conflict | Duplicate create, resource already in terminal state |
| `422` Unprocessable Entity | Valid format, failed validation | Missing required field, value out of range |
| `429` Too Many Requests | Rate limit exceeded | Include `Retry-After` header |
| `500` Internal Server Error | Unhandled exception | Log full stack trace server-side; return safe message only |
| `501` Not Implemented | Endpoint defined, not yet built | Planned endpoints |
| `502` Bad Gateway | Upstream dependency returned an error | External service call failed |
| `503` Service Unavailable | System overloaded or dependency down | Include `Retry-After` header if recoverable |

Error response body:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "SCREAMING_SNAKE_CASE",
    "message": "Human-readable description safe to show a client",
    "details": [
      { "field": "email", "issue": "must be a valid email address" }
    ]
  }
}
```

- `code` is machine-readable, used by clients for programmatic handling
- `message` never exposes stack traces, internal IDs, or SQL
- `details` populated for `422` validation errors — one entry per failing field

### Endpoint Completeness

A `POST` that creates a resource implies the full CRUD set. All four must be accounted for — they can ship separately but must all be planned:

| Operation | Method | Path |
|-----------|--------|------|
| Create | `POST` | `/api/v1/resources` |
| Read (single) | `GET` | `/api/v1/resources/{id}` |
| Read (list) | `GET` | `/api/v1/resources` |
| Update | `PUT` | `/api/v1/resources/{id}` |
| Delete | `DELETE` | `/api/v1/resources/{id}` |

If any operation is intentionally omitted, document why.

---

## Part 2 — Review

### Step 1 — Locate the contract

```bash
grep -ril "openapi:" --include="*.yaml" --include="*.yml" --include="*.json" . 2>/dev/null | head -5
find . -name "*.proto" 2>/dev/null | head -5
```

### Step 2 — Completeness check

- [ ] All CRUD operations represented (or explicitly omitted with justification)
- [ ] All resource states covered (created, updated, deleted, error states)
- [ ] Pagination defined for list endpoints (cursor-based preferred over offset)
- [ ] Filtering and sorting parameters documented
- [ ] Bulk operations defined if needed (batch create/update)

### Step 3 — HTTP semantics (REST)

| Concern | Requirement |
|---------|-------------|
| Methods | GET (idempotent, no body), POST (create), PUT (full replace), PATCH (partial update), DELETE |
| Status codes | 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500 — per the table above |
| Content-Type | `application/json` for request and response bodies |
| Idempotency | PUT and DELETE must be idempotent; PATCH should be |
| Versioning | URL prefix (`/v1/`) or `Accept` header — must be consistent across all endpoints |

### Step 4 — Security review

- [ ] Authentication required on all non-public endpoints (`401` on missing/invalid token)
- [ ] Authorisation scopes or roles documented for each endpoint
- [ ] Rate limiting documented (or noted as infrastructure-level)
- [ ] HTTPS-only — no HTTP endpoints
- [ ] Sensitive fields not returned unnecessarily (passwords, internal IDs, PII)
- [ ] CORS policy defined if consumed from browser
- [ ] `403` returned when authenticated but unauthorised (not `404`)

### Step 5 — Error format

- [ ] Error schema is consistent across all endpoints
- [ ] Error messages do not expose stack traces, internal IDs, or implementation details
- [ ] `code` field is machine-readable (SCREAMING_SNAKE_CASE)
- [ ] Validation errors include the offending field and a fix hint

### Step 6 — Schema and type correctness

- [ ] All request/response fields typed correctly (string, integer, boolean, array, object)
- [ ] Date/time fields use ISO 8601 format (`2024-01-15T10:30:00Z`)
- [ ] UUIDs typed as `string` with `format: uuid`
- [ ] Monetary values as integers (cents) or `string` — never `number`
- [ ] Required vs optional fields explicitly declared
- [ ] Nullable fields explicitly marked
- [ ] Enum values documented with business meaning

### Step 7 — Business alignment

- [ ] Field names match the domain ubiquitous language (not DB column names)
- [ ] Response payloads include only data the consumer needs (no over-fetching)
- [ ] Breaking changes flagged (removed fields, changed types, renamed fields, status code changes)
- [ ] Backwards-compatible changes noted (added optional fields, new endpoints)
- [ ] Consumer use cases validated: can all known consumers complete their workflows?

### Step 8 — gRPC specific (if applicable)

- [ ] Proto3 syntax used
- [ ] Service and RPC names in PascalCase, field names in snake_case
- [ ] Streaming RPCs justified (unary is default)
- [ ] Error status codes use `google.rpc.Status`
- [ ] `google.protobuf.FieldMask` for partial updates
- [ ] Package and option declarations set correctly

### Step 9 — Output the review

```
# API Review: <API Name / Version>

## Summary
<1-3 sentence overall assessment>

## Findings

| # | Severity | Category | Endpoint / Field | Issue | Recommendation |
|---|----------|----------|-----------------|-------|----------------|
| 1 | Critical  | Security | DELETE /users/{id} | No authorisation scope documented | Add `admin:users` scope requirement |
| 2 | High      | HTTP     | POST /orders | Returns 200 on creation | Change to 201 Created |
| 3 | Medium    | Schema   | amount field | Typed as `number` (float risk) | Change to `integer` (cents) |
| 4 | Low       | Naming   | user_id field | Does not match ubiquitous language | Rename to `customerId` |

## Breaking Changes
<List any breaking changes vs previous version>

## Approved / Blocked
<APPROVED — ready for implementation | BLOCKED — must fix Critical/High findings first>
```

### Severity definitions

| Severity | Meaning |
|----------|---------|
| Critical | Security vulnerability, data exposure, or auth bypass |
| High | Incorrect HTTP semantics, data corruption risk |
| Medium | Inconsistency, missing documentation, schema issue |
| Low | Naming, style, or minor improvement |
