---
name: test-plan
description: Given a feature or user story, produce a structured test plan covering unit, integration, E2E, performance, and security testing scope.
---

# Test Plan Skill

Produce a structured test plan for a feature or user story before tests are written. Use this to align the team on what is being tested, at which layer, with what data.

## Step 1 — Understand the feature

Read:
- The user story or feature description
- Acceptance criteria (Given/When/Then)
- Related API contract or UI mockup
- Existing tests in the area (to avoid duplication)

```bash
# Find existing tests in the area
find src/test/java -name "*Test*.java" 2>/dev/null
find src -name "*.test.ts" 2>/dev/null
find src/test/resources/features -name "*.feature" 2>/dev/null
```

## Step 2 — Risk identification

List the highest-risk areas:
- New integrations with external systems
- Security boundaries (authentication, authorisation, data access)
- Complex business logic or edge cases
- Performance-sensitive paths (high-traffic endpoints, large data sets)
- Error paths and compensating transactions

## Step 3 — Define test scope by layer

| Layer | Scope | Coverage target | Tools |
|-------|-------|----------------|-------|
| Unit | Business logic in isolation: domain entities, use cases, utilities | ≥90% | JUnit 5 / pytest / Vitest |
| Integration | Component interactions: API → service → repository → real DB | ≥80% | Testcontainers / RestAssured |
| E2E | Critical user journeys end to end | 100% of critical paths | Playwright / Cypress / Appium |
| Performance | High-traffic endpoints under load | P95 < 200ms (read), < 500ms (write) | Gatling / k6 |
| Security | OWASP Top 10 for new endpoints | All critical paths | ZAP / Burp / manual |
| Contract | API compatibility with consumers | All consumer contracts | Pact |

Only include layers relevant to the feature — a configuration change may need only unit tests; a new public API needs all layers.

## Step 4 — Scenario matrix

List test scenarios by type:

**Positive scenarios** (happy path):
- [ ] Scenario: what the feature does when used correctly

**Negative scenarios** (error path):
- [ ] Invalid input: missing required field, wrong type, out-of-range value
- [ ] Unauthorised access: unauthenticated, insufficient scope/role
- [ ] Not found: resource does not exist
- [ ] Conflict: duplicate resource, state machine violation

**Edge cases**:
- [ ] Boundary values (zero, max, empty string, null)
- [ ] Concurrent operations (race conditions, optimistic lock violations)
- [ ] Large payloads or lists (pagination, size limits)
- [ ] Idempotency (same request twice)

**Performance scenarios** (if applicable):
- [ ] Normal load (expected RPS)
- [ ] Peak load (2× expected)
- [ ] Sustained load (60-minute soak test)

## Step 5 — Test data strategy

Define how test data is created and managed:

| Type | Strategy |
|------|----------|
| Unit | In-memory fixtures, object builders/mothers |
| Integration | Database seeded in `@BeforeEach`, rolled back in `@AfterEach` |
| E2E | Dedicated test environment, seeded via API or migration script |
| Performance | Realistic data volume (≥1M rows in DB, representative payload sizes) |

Rules:
- Never use production data
- Never hardcode test data — use factories or builders
- Test data must not persist across test runs (use transactions or truncation)
- PII must be anonymised or synthetic

## Step 6 — Entry and exit criteria

**Entry criteria** (must be true before testing begins):
- [ ] Acceptance criteria written in Given/When/Then
- [ ] API contract reviewed and approved
- [ ] Development environment stable and seeded
- [ ] Required test data available

**Exit criteria** (must be true before marking done):
- [ ] All test scenarios executed (no skipped)
- [ ] Coverage targets met (≥90% unit, ≥80% integration)
- [ ] Zero open Critical or High defects
- [ ] Performance targets met (P95 within SLA)
- [ ] Security findings addressed

## Step 7 — Output the test plan

```
# Test Plan: <Feature Name>

## Scope
<Feature description and acceptance criteria summary>

## Risk Areas
<Numbered list of highest-risk areas>

## Test Layers
<Table from Step 3 with only relevant layers>

## Scenario Matrix
<Positive, negative, edge case, performance scenarios>

## Test Data Strategy
<How data is created, managed, and cleaned up>

## Entry Criteria
<Checklist>

## Exit Criteria
<Checklist>

## Estimated Effort
<Story points or hours per layer>
```
