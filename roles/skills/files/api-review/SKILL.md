---
name: api-review
description: Review an API contract (OpenAPI/REST/gRPC) for correctness, security, and business alignment.
---

# API Review Skill

Review an API contract before implementation or before merge. Use this for REST (OpenAPI 3.1) and gRPC (proto3) contracts.

## Step 1 — Locate the contract

```bash
grep -ril "openapi:" --include="*.yaml" --include="*.yml" --include="*.json" . 2>/dev/null | head -5
find . -name "*.proto" 2>/dev/null | head -5
```

## Step 2 — Completeness check

- [ ] All CRUD operations represented (or explicitly omitted with justification)
- [ ] All resource states covered (created, updated, deleted, error states)
- [ ] Pagination defined for list endpoints (cursor-based preferred over offset)
- [ ] Filtering and sorting parameters documented
- [ ] Bulk operations defined if needed (batch create/update)

## Step 3 — HTTP semantics (REST)

| Concern | Requirement |
|---------|-------------|
| Methods | GET (idempotent, no body), POST (create), PUT (full replace), PATCH (partial update), DELETE |
| Status codes | 200 (ok), 201 (created), 204 (no content), 400 (bad request), 401 (unauthenticated), 403 (forbidden), 404 (not found), 409 (conflict), 422 (validation), 429 (rate limited), 500 (server error) |
| Content-Type | `application/json` for request and response bodies |
| Idempotency | PUT and DELETE must be idempotent; PATCH should be |
| Versioning | URL prefix (`/v1/`) or `Accept` header — must be consistent across all endpoints |

## Step 4 — Security review

- [ ] Authentication required on all non-public endpoints (`401` on missing/invalid token)
- [ ] Authorisation scopes or roles documented for each endpoint
- [ ] Rate limiting documented (or noted as infrastructure-level)
- [ ] HTTPS-only — no HTTP endpoints
- [ ] Sensitive fields not returned unnecessarily (passwords, internal IDs, PII)
- [ ] CORS policy defined if consumed from browser
- [ ] `403` returned when authenticated but unauthorised (not `404`)

## Step 5 — Error format

All error responses must use a consistent schema:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Human-readable description",
  "details": [
    { "field": "email", "issue": "must be a valid email address" }
  ]
}
```

- [ ] Error schema is consistent across all endpoints
- [ ] Error messages do not expose stack traces, internal IDs, or implementation details
- [ ] `code` field is machine-readable (SCREAMING_SNAKE_CASE)
- [ ] Validation errors include the offending field and a fix hint

## Step 6 — Schema and type correctness

- [ ] All request/response fields typed correctly (string, integer, boolean, array, object)
- [ ] Date/time fields use ISO 8601 format (`2024-01-15T10:30:00Z`)
- [ ] UUIDs typed as `string` with `format: uuid`
- [ ] Monetary values as integers (cents) or `string` (to avoid float precision issues) — never `number`
- [ ] Required vs optional fields explicitly declared
- [ ] Nullable fields explicitly marked (`nullable: true` or `null` in union type)
- [ ] Enum values documented with business meaning

## Step 7 — Business alignment

- [ ] Field names match the domain ubiquitous language (not DB column names)
- [ ] Response payloads include only data the consumer needs (no over-fetching)
- [ ] Breaking changes flagged (removed fields, changed types, renamed fields, status code changes)
- [ ] Backwards-compatible changes noted (added optional fields, new endpoints)
- [ ] Consumer use cases validated: can all known consumers complete their workflows with this API?

## Step 8 — gRPC specific (if applicable)

- [ ] Proto3 syntax used
- [ ] Service and RPC names in PascalCase, field names in snake_case
- [ ] Streaming RPCs justified (unary is default; server/client/bidi streaming for specific use cases)
- [ ] Error status codes use `google.rpc.Status`
- [ ] `google.protobuf.FieldMask` for partial updates
- [ ] Package and option declarations set correctly

## Step 9 — Output the review

Produce a review with these sections:

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

## Severity definitions

| Severity | Meaning |
|----------|---------|
| Critical | Security vulnerability, data exposure, or auth bypass |
| High | Incorrect HTTP semantics, data corruption risk |
| Medium | Inconsistency, missing documentation, schema issue |
| Low | Naming, style, or minor UX improvement |
