---
name: threat-model
description: Produce a STRIDE threat model for a feature, component, or system boundary.
---

# Threat Model Skill

Produce a structured STRIDE threat model. Use this skill at the start of any new feature, integration, or architecture change.

## Step 1 — Define the scope

State what you are modelling:
- **Feature / component**: Name and brief description
- **System boundary**: What is inside vs outside the scope
- **Actors**: Who interacts with it (user, admin, external service, background job)
- **Entry points**: APIs, UI forms, message queue topics, file uploads, webhooks
- **Assets**: What data or capabilities need protection (PII, credentials, financial data, admin operations)

## Step 2 — Draw the data flow (text format)

```
[Actor] → [Entry Point] → [Component] → [Data Store / Downstream Service]
```

Example:
```
[Browser] → POST /api/auth/login → [AuthService] → [UserRepository → PostgreSQL]
[AuthService] → [JWT issued to browser]
```

## Step 3 — Apply STRIDE to each component and data flow

For each arrow or component in the data flow, identify applicable threats:

| Threat | Question to ask |
|--------|----------------|
| **S**poofing | Can an attacker impersonate a legitimate actor or component? |
| **T**ampering | Can data in transit or at rest be modified without detection? |
| **R**epudiation | Can a user deny an action? Is there an audit trail? |
| **I**nformation Disclosure | Can sensitive data be exposed to unauthorized parties? |
| **D**enial of Service | Can an attacker exhaust resources or disrupt availability? |
| **E**levation of Privilege | Can an attacker gain higher permissions than granted? |

## Step 4 — Risk assessment

Rate each identified threat:

| Threat | STRIDE | Likelihood (L/M/H) | Impact (L/M/H) | Risk | Mitigation |
|--------|--------|-------------------|----------------|------|------------|
| Login brute force | S, DoS | High | High | Critical | Rate limit: 5 attempts → 15 min lockout |
| JWT algorithm confusion | S, EoP | Low | Critical | High | Reject `none`; fix algorithm in decoder |
| Verbose error leaks stack trace | I | Medium | Medium | Medium | Return generic error messages |

**Risk matrix**: High × High = Critical, High × Low = High, Low × Low = Low

## Step 5 — Define mitigations

For each Medium/High/Critical risk, specify:
- **Control**: What technical control addresses the threat
- **Layer**: Where the control is applied (network, application, data, identity)
- **Owner**: Which agent / team implements it
- **Validation**: How to verify the control is effective (test, scan, review)

## Step 6 — Output the threat model document

Produce a document with these sections:

```
# Threat Model: <Feature/Component>

## Scope
<What is being modelled>

## Data Flow
<Text diagram>

## STRIDE Analysis
<Table from Step 3>

## Risk Assessment
<Table from Step 4>

## Mitigations
<Table from Step 5>

## Residual Risks
<Accepted risks with justification and review date>
```

## Safety rules

- Model threats for new features BEFORE implementation
- Residual risks must be explicitly accepted — not silently ignored
- Update the threat model when the architecture changes
- Share the threat model with secops-engineer and identity-security-developer for review
- If the scope includes OAuth2, OIDC, or JWT flows, use [/oauth-threat-model](../oauth-threat-model/SKILL.md) instead — it has pre-populated threat tables for those attack surfaces
