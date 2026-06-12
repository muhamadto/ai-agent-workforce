---
name: business-analysis
description: Reference knowledge for business analysis — requirements elicitation techniques, INVEST user stories, Given/When/Then acceptance criteria, event storming and ubiquitous language, BPMN process mapping, gap analysis, prioritisation frameworks (MoSCoW, RICE, Kano), defect vs enhancement classification, Definition of Ready/Done, and stakeholder sign-off. Load this BEFORE gathering requirements, writing or refining user stories, modeling a domain, or mapping a business process.
---

# Business Analysis Reference

Reference knowledge for requirements work. Load this skill before eliciting requirements, writing user stories, modeling domains, or mapping processes.

## Requirements Elicitation

- **Stakeholder interviews**: Structured questioning to surface explicit and implicit needs
- **As-is / To-be analysis**: Document current state, define future state, identify gaps
- **Observation**: Watch users work to uncover unstated needs and pain points
- **Document analysis**: Extract requirements from existing specs, contracts, compliance mandates
- **Workshops**: Facilitate collaborative sessions to align stakeholders and resolve conflicts
- **Prototyping**: Low-fidelity wireframes and mockups to validate understanding early

## User Story Format (INVEST)

```
As a <role>,
I want to <action/goal>,
So that <business value/benefit>.
```

**INVEST criteria** — every story must be:
- **Independent**: Deliverable without depending on another story
- **Negotiable**: Details can be refined, not a rigid contract
- **Valuable**: Delivers direct benefit to a user or business
- **Estimable**: Team can estimate size with reasonable confidence
- **Small**: Completable within one sprint (2 weeks max)
- **Testable**: Clear pass/fail criteria exist

## Acceptance Criteria (Given/When/Then)

```gherkin
Feature: User password reset

  Scenario: Successful password reset via email
    Given the user is registered with email "user@example.com"
    And the user is not currently logged in
    When the user requests a password reset for "user@example.com"
    Then a reset link is sent to "user@example.com"
    And the link expires after 1 hour
    And the user can set a new password using the link

  Scenario: Password reset requested for unknown email
    Given no account exists for "unknown@example.com"
    When the user requests a password reset for "unknown@example.com"
    Then no email is sent
    And the response gives no indication whether the email is registered
    # (prevents user enumeration — security requirement)
```

- **Positive scenarios**: Happy path — what should work
- **Negative scenarios**: What should fail, and how it should fail
- **Edge cases**: Boundary values, empty inputs, concurrent actions
- **Security constraints**: Encode security requirements as explicit criteria
- **Non-functional requirements (NFRs)**: Performance, availability, accessibility as criteria

## Domain Modeling

### Event Storming (Collaborative Discovery)

1. **Domain Events**: What happened? (past tense: `OrderPlaced`, `PaymentFailed`)
2. **Commands**: What triggered it? (`PlaceOrder`, `ProcessPayment`)
3. **Actors**: Who triggered the command? (User, System, External service)
4. **Aggregates**: What data/invariants are involved?
5. **Bounded Contexts**: Where do domain models diverge?

### Ubiquitous Language

- **One term, one meaning**: No synonyms within a bounded context
- **Glossary**: Maintain a domain glossary accessible to the whole team
- **Code reflects domain**: Class names, method names match the domain language
- **Challenge ambiguity**: When stakeholders use different words for the same thing — align immediately

## Process Mapping

### BPMN (Business Process Model and Notation)

- **Start/end events**: Process boundaries
- **Tasks**: Atomic work units (human or automated)
- **Gateways**: Decisions (exclusive, inclusive, parallel)
- **Swim lanes**: Responsibility boundaries (roles, systems)
- **Message flows**: Cross-boundary communication

### Process Documentation

```
Current State (As-Is):
  1. Customer submits paper form → 2. Clerk manually enters data → 3. Manager reviews printout → 4. Approval emailed back (3-5 days)

Pain Points:
  - Manual data entry (error-prone)
  - No audit trail
  - Slow approval cycle

Future State (To-Be):
  1. Customer submits online form → 2. Automated validation → 3. Manager approves in system → 4. Instant notification (< 1 hour)

Benefits:
  - Eliminate manual entry errors
  - Full audit trail
  - 95% reduction in approval time
```

## Gap Analysis

| Requirement | Current Capability | Gap | Priority | Effort |
|-------------|-------------------|-----|----------|--------|
| Real-time notifications | Polling every 5 min | Latency too high | High | Medium |
| Multi-currency support | USD only | Cannot serve EU market | High | High |
| Audit trail | No logging | Compliance failure | Critical | Low |

## Prioritisation Frameworks

### MoSCoW

- **Must have**: Non-negotiable — system fails without it
- **Should have**: Important but not critical for launch
- **Could have**: Nice-to-have, include if capacity allows
- **Won't have (this time)**: Explicitly out of scope for current iteration

### RICE Scoring

```
RICE Score = (Reach × Impact × Confidence) / Effort

Reach:     users affected per quarter
Impact:    1 (minimal) → 3 (massive)
Confidence: 0-100% (how sure are we of estimates)
Effort:    person-weeks to deliver
```

### Kano Model

- **Basic needs**: Expected — not having them causes dissatisfaction
- **Performance needs**: Linear relationship — more is better
- **Excitement needs**: Unexpected delights — differentiators
- **Indifferent**: Nice to know but users don't care either way

## Defect vs Enhancement

| Defect | Enhancement |
|--------|-------------|
| System does not meet agreed acceptance criteria | New capability beyond agreed scope |
| Existing behaviour broken | Change to working behaviour |
| Fix at current sprint priority | Backlog and prioritise |

## Stakeholder Communication

### Requirement Sign-Off

- Written acceptance of requirements before development begins
- Changes after sign-off follow a change request process
- Stakeholders informed of impact: scope, timeline, cost

### Definition of Ready (DoR)

Criteria a story must meet before entering a sprint:

- [ ] Story has clear business value
- [ ] Acceptance criteria written in Given/When/Then
- [ ] Dependencies identified and resolved
- [ ] Team has estimated (story points)
- [ ] Design/mockup reviewed (if UI)

### Definition of Done (DoD)

Criteria a story must meet to be marked complete:

- [ ] Acceptance criteria verified by QE
- [ ] Code reviewed and merged
- [ ] Deployed to staging environment
- [ ] Product owner accepted

### Conflict Resolution

1. Surface conflicting requirements explicitly — don't resolve silently
2. Bring stakeholders together to align (not email chains)
3. Document the decision and rationale
4. Update requirements, acceptance criteria, and the backlog

## API Contract Review

Review API contracts for business alignment — verify field names match the domain ubiquitous language, response payloads match consumer use cases, and breaking changes are flagged.

## Artefacts Produced

| Artefact | Purpose |
|----------|---------|
| User Story | Requirement in deliverable unit |
| Acceptance Criteria (Gherkin) | Testable pass/fail conditions |
| Domain Glossary | Shared language across teams |
| Process Map (BPMN) | Visual workflow documentation |
| Gap Analysis | Current vs desired capability |
| API Contract Review | Business alignment with technical spec |
| Prioritised Backlog | Development order with rationale |
| Release Notes | Business-readable change summary |

## Related Skills

- [/api-design](../api-design/SKILL.md) — review API contracts against HTTP semantics and business alignment
- [/test-plan](../test-plan/SKILL.md) — turn acceptance criteria into a structured test plan
- [/adr](../adr/SKILL.md) — document decisions and rationale that resolve requirement conflicts
- [/spike](../spike/SKILL.md) — time-boxed research when feasibility is unknown
