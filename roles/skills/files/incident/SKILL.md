---
name: incident
description: Guide incident response from detection through resolution, and produce a blameless postmortem document.
---

# Incident Skill

Structured incident response: detect, contain, resolve, communicate, and document. Produce a blameless postmortem when the incident is closed.

## When to use

- A production issue has been detected and needs a coordinated response
- The incident is resolved and a postmortem is required
- Reviewing an existing postmortem for completeness

---

## Phase 1 — Detect and declare

### 1.1 — Declare the incident

Assign a severity:

| Severity | Criteria | Response SLA |
|----------|----------|-------------|
| SEV-1 | Complete outage, data loss, or security breach | Immediate — all hands |
| SEV-2 | Major feature unavailable, significant user impact | < 15 min response |
| SEV-3 | Degraded performance, minor feature impaired | < 1 hour response |
| SEV-4 | Cosmetic or low-impact issue | Business hours |

### 1.2 — Assign roles

| Role | Responsibility |
|------|---------------|
| **Incident Commander (IC)** | Owns the incident; coordinates the response; makes decisions |
| **Technical Lead** | Investigates root cause; proposes and implements fixes |
| **Communications Lead** | Updates stakeholders and status page |
| **Scribe** | Records timeline, actions, and decisions in real time |

---

## Phase 2 — Investigate

### 2.1 — Gather signals

```bash
# Check recent deployments
git log --oneline --since="2 hours ago" origin/main

# Check error rates (adapt to your observability stack)
# Prometheus / Grafana — check error rate and latency dashboards
# Loki / ELK — search for ERROR/FATAL in the last 30 minutes
```

Timeline questions to answer immediately:
- When did the issue start? (first alert timestamp)
- What changed recently? (deploy, config change, traffic spike)
- What is the blast radius? (all users / subset / one region)
- Are there related alerts firing?

### 2.2 — Form a hypothesis

Write one sentence: "We believe `<component>` is failing because `<cause>`, causing `<impact>`."

Update this as evidence changes. Do not chase multiple hypotheses simultaneously.

---

## Phase 3 — Contain and mitigate

Take the fastest action to limit user impact — even if it is not the root-cause fix:

| Mitigation | When to use |
|------------|------------|
| Roll back the last deployment | Issue started after a deploy |
| Toggle feature flag off | Feature-gated code is the suspect |
| Increase pod/instance count | Capacity issue |
| Enable maintenance mode | Prevents further data corruption |
| Failover to replica | Primary DB degraded |
| Block offending traffic | DDoS / abuse pattern |

Document every mitigation action with a timestamp in the incident channel.

---

## Phase 4 — Communicate

### Internal updates (every 30 min for SEV-1/2)

```text
[HH:MM UTC] Status: Investigating / Mitigating / Resolved
Impact: <what users experience>
Current hypothesis: <one sentence>
Next update: HH:MM UTC
```

### External status page (for user-visible incidents)

```text
We are investigating reports of <impact>. Our team is working to resolve
this as quickly as possible. We will provide an update by HH:MM UTC.
```

---

## Phase 5 — Resolve and close

Checklist before declaring resolved:
- [ ] Root cause identified
- [ ] Fix deployed and verified in production
- [ ] Error rate and latency back to baseline
- [ ] No dependent systems still affected
- [ ] Stakeholders notified of resolution
- [ ] Incident channel archived / ticket closed

---

## Phase 6 — Postmortem

Write the postmortem within 48 hours while memory is fresh. Save to `docs/postmortems/YYYY-MM-DD-<slug>.md`.

```markdown
# Postmortem: <Title>

**Date:** YYYY-MM-DD
**Severity:** SEV-N
**Duration:** HH:MM (from detection to resolution)
**Author(s):** <names>
**Status:** Draft | In Review | Final

---

## Summary

<2–3 sentences: what happened, blast radius, and how it was resolved>

---

## Timeline (all times UTC)

| Time | Event |
|------|-------|
| HH:MM | First alert fired |
| HH:MM | Incident declared, IC assigned |
| HH:MM | Hypothesis: <one sentence> |
| HH:MM | Mitigation applied: <action> |
| HH:MM | Root cause confirmed |
| HH:MM | Fix deployed |
| HH:MM | Incident resolved |

---

## Root Cause

<Detailed technical explanation of what went wrong and why.
Use the 5-Whys technique to reach the systemic root cause, not just the proximate trigger.>

**5 Whys:**
1. Why? <proximate cause>
2. Why? <one level deeper>
3. Why? <one level deeper>
4. Why? <one level deeper>
5. Why? <systemic root cause>

---

## Impact

- **Users affected:** <number or percentage>
- **Duration:** <HH:MM>
- **Data loss:** <yes/no — describe if yes>
- **SLA breach:** <yes/no>
- **Revenue impact:** <estimate if applicable>

---

## What Went Well

- <detection was fast>
- <rollback worked cleanly>

---

## What Could Be Improved

- <alert threshold was too sensitive / not sensitive enough>
- <runbook was missing>

---

## Action Items

| Action | Owner | Due |
|--------|-------|-----|
| Add alert for <X> | @name | YYYY-MM-DD |
| Write runbook for <scenario> | @name | YYYY-MM-DD |
| Fix root cause: <description> | @name | YYYY-MM-DD |
| Add integration test for <scenario> | @name | YYYY-MM-DD |

---

## Lessons Learned

<One paragraph on what the team learned and how it changes future behaviour>
```

---

## Safety rules

- Postmortems are blameless — focus on systems and processes, never individuals
- Never publish a postmortem externally before legal/comms review for SEV-1 incidents
- All action items must have an owner and a due date — unowned items rot
- Close all action items within 30 days or escalate
- Never delete or edit a postmortem after it is marked Final — append an addendum instead
