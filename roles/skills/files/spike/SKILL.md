---
name: spike
description: Document a technical spike — time-boxed research into a technical question — with findings, recommendation, and a clear go/no-go outcome.
---

# Spike Skill

Structure and document a time-boxed technical investigation. A spike answers a specific technical question so the team can make an informed decision without over-building.

## When to use

- There is uncertainty about a technical approach that blocks story estimation
- Two or more viable solutions exist and the trade-offs are unclear
- A new library, framework, or API needs to be evaluated before adopting
- A performance or scalability question needs empirical answers

---

## Step 1 — Define the spike

Before starting, answer these questions in writing:

```markdown
## Spike: <Title>

**Question:** <The specific, answerable technical question this spike addresses>
**Timebox:** <Duration — e.g. 4 hours, 1 day, 2 days max>
**Owner:** <Who is doing the spike>
**Definition of Done:** <What output will close this spike>
```

A good spike question is narrow and answerable:
- ✅ "Can we achieve < 50ms P99 on the search endpoint using PostgreSQL full-text search with GIN indexes on a 10M-row dataset?"
- ✅ "Does Keycloak support multi-tenant realm isolation with per-tenant password policies out of the box?"
- ❌ "Should we use PostgreSQL or Elasticsearch?" — too broad, not answerable without first scoping it

**Definition of Done** must be one of:
- A proof-of-concept with measured results
- A go/no-go recommendation with evidence
- An estimate or story breakdown for the actual implementation

---

## Step 2 — Investigate

Work within the timebox. Document findings as you go — do not wait until the end.

Typical activities:
- Read official documentation and changelogs
- Run a minimal proof-of-concept
- Measure performance with representative data
- Identify integration points and failure modes
- Check community health (maintenance, open issues, adoption)

If the timebox expires before a conclusion is reached, stop and report partial findings. Do not extend the spike without explicit team agreement.

---

## Step 3 — Write the spike report

Save to `docs/spikes/YYYY-MM-DD-<slug>.md`:

```markdown
# Spike: <Title>

**Date:** YYYY-MM-DD
**Owner:** <name>
**Timebox:** <duration>
**Status:** In Progress | Complete | Abandoned

---

## Question

<The exact question this spike was meant to answer>

---

## Context

<Why this question needed to be answered now. What story or decision depends on it?>

---

## Approach

<What was investigated and how. Include tools used, datasets, and any PoC code written.>

---

## Findings

<Factual observations from the investigation. Measurements, limitations, surprises.>

### Option 1: <name>

**Pros:**
- <pro>

**Cons:**
- <con>

**Measured results:** <latency, throughput, complexity score, etc.>

### Option 2: <name>

**Pros:**
- <pro>

**Cons:**
- <con>

**Measured results:**

---

## Recommendation

**Go / No-Go / Needs more investigation**

We recommend **<option>** because **<one-sentence rationale>**.

<2–3 sentences explaining the trade-off and why this option fits the constraints.>

---

## Implementation notes

<Key implementation considerations the team should know before starting the actual story.
Include gotchas, migration steps, or dependencies to set up.>

---

## Open questions

- <question that this spike could not answer within the timebox>

---

## PoC code / references

- Link to branch, PR, or notebook containing PoC code
- Links to relevant docs, benchmarks, or prior art
```

---

## Step 4 — Present findings

Share the spike report with the team before the next planning session. The outcome must feed directly into:
- A story being added to the backlog (if Go)
- A decision recorded in an ADR (use the [/adr](../adr/SKILL.md) skill)
- A risk item added to the project risk register (if No-Go or Needs more investigation)

---

## Safety rules

- Never extend the timebox without team agreement — a spike that runs indefinitely is just unplanned work
- Never ship PoC code to production — it exists only to answer the question
- Always produce a written artefact — verbal "I looked into it" does not count
- If the spike reveals the question cannot be answered without building more infrastructure, that is a valid finding — escalate it, do not keep digging
- Link the spike report from the originating story or ADR so context is preserved
