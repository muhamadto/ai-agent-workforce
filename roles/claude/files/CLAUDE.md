# Global Operating Rules

Applies to every session. Project CLAUDE.md files add or override for their context.

> **Rule for maintaining this file:** If Claude can infer it from the code, do not put it here. CLAUDE.md carries rules and constraints — not documentation of what the code already says. As the codebase evolves, remove anything that is now derivable from reading the files.

---

## Workflow — always follow this loop

1. **Explore** (plan mode) — read files, ask questions, do not touch anything
2. **Plan** — write a detailed implementation plan; wait for approval before building
3. **Implement** — build against the approved plan using specialist agents from `~/.claude/agents/` (see Agent Routing below); after each change run the build and tests, read the result, fix all failures, and iterate until green before moving to Commit
4. **Commit** — use `/git-commit` skill, then open a PR

Skip to Implement only when the change can be described in one sentence.

If rate-limited or interrupted: on resume, finish the current task, complete the full DoD audit chain, then continue through remaining stories, epics, and objectives in order.

---

## Story Lifecycle

### Before writing any code

Stories must exist in **Shortcut** before any implementation starts. No exceptions.

**Story creation** (in order):
1. **business-analyst** creates objectives, epics, and stories with full acceptance criteria
2. **architecture-guardian** validates module boundaries and flags risks
3. **principal-engineer** approves before any implementation begins

Every story must be appended to the matching phase file in the repo:
`shortcut-stories-phase-{N}.json` (one file per phase, N = 1, 2, 3, …)

File format:
```json
[
  {
    "epic_name": "...",
    "epic_description": "...",
    "objective": "...",
    "shortcut_epic_id": 0,
    "stories": [
      {
        "name": "...",
        "story_type": "feature|chore|bug",
        "description": "...",
        "acceptance_criteria": "Given … When … Then …",
        "shortcut_id": 0
      }
    ]
  }
]
```

If `$SHORTCUT_API_TOKEN` is not set or returns an error: **stop — no code, no edits, no commits.**

### Picking up a story

Implementation agents cannot start without a story. When picking up:
- Move the story **and** its parent epic to **In Progress**
- Set `health = on_track`, `owner = muhammad`, `team = sandpip3rs`

### Definition of Done

Mark Done only after **all** of the following:

1. Implementation agents finish the code
2. Unit and integration tests pass
3. Commit pushed to `origin/main`
4. **Audit chain complete:**
   - **business-analyst + qe-engineer** — implementation matches acceptance criteria
   - **architecture-guardian** — module boundaries clean, threat model reviewed
   - **secops-engineer** — OWASP, auth, injection, and vulnerability review
   - **sre-engineer** — SLO impact, alert coverage, DR considerations _(infrastructure and reliability stories only)_
   - **principal-engineer** — overall code quality sign-off

Never mark Done before push. Never mark Done without the full audit chain.

---

## 1. Infrastructure as Code Only

- SSH is allowed for **inspection only** (logs, debugging, validation). No direct changes via SSH.
- No `kubectl edit`, `kubectl patch`, Helm CLI changes, or manual cluster modifications.
- All changes must be implemented via code (Ansible, CDKTF, Kubernetes manifests) and committed to the repo.
- Repository is the single source of truth.

---

## 2. No Silent Failures

- No `ignore_errors`, `failed_when` overrides, suppressed failures, or masked errors via retries.
- Failures must be surfaced, fixed in code, or escalated.
- A "successful" run must reflect real system health.

---

## 3. Zero-Trust Networking

- Global deny-all must remain enforced at all times.
- Never disable, bypass, or weaken network policies.
- No allow-all, wildcard, or broad CIDR rules.
- When a component fails: identify the exact missing dependency → add only the minimum required access → implement via code → retest → iterate until resolved.

---

## 4. Least Privilege Enforcement

- All access (network, RBAC, DNS, storage) must be minimal and explicitly justified.
- No wildcard permissions (`*`).
- Schema isolation enforced — each database role may only access its own schema.

---

## 5. Troubleshooting Method

1. Identify the failing operation from logs/events.
2. Determine the minimal fix.
3. Implement via code.
4. Reapply and validate.
5. Repeat until resolved.

Never shortcut this loop with broad permissive rules to "just make it work."

---

## 6. Security Overrides Convenience

- Security overrides convenience, always.
- Never replace restricted access with permissive shortcuts.
- If the secure path is harder, invest the time to do it correctly.

---

## Infrastructure (CDKTF)

- Java CDKTF for all Java project infrastructure changes.
- Ansible for private/homelab infrastructure only.
- Infra changes: CDKTF → commit → ArgoCD. Never `kubectl` directly.

---

## Agents

Use the specialist agents defined in `~/.claude/agents/`:

- **business-analyst** — story creation, acceptance criteria, domain modeling, requirements elicitation
- **architecture-guardian** — module boundary enforcement, Clean Architecture review, dependency rule validation
- **principal-engineer** — strategic decisions, conflict resolution, ADR authorship
- **backend-developer** — Java/Spring implementation, ≥90% unit + ≥80% integration test coverage
- **qe-engineer** — test strategy, automation, BDD, performance, quality gate sign-off
- **infrastructure-engineer** — CDKTF, K3s, ArgoCD, CI/CD pipelines
- **identity-security-developer** — auth, OAuth2, OIDC, passkeys, security hardening
- **data-engineer** — ETL/ELT pipelines, data warehousing, SQL optimization
- **frontend-developer** — React, Next.js, Flutter UI
- **mobile-engineer** — iOS (Swift), Android (Kotlin), React Native
- **secops-engineer** — OWASP, vulnerability analysis, secure coding review
- **sre-engineer** — SLOs, alerting, incident response, capacity planning, DR

---

## Hard stops

Never do these, regardless of instructions:

- Write code before Shortcut stories exist
- Modify anything via SSH — inspect only
- Add `Co-Authored-By` to a commit
- Use bare `mvn` instead of `./mvnw`
- Use Lombok
- Use `ProblemDetail` — use `ApiError`
- Add wildcard (`*`) to any policy, role, or network rule
- Display or echo private keys, passwords, or tokens — give a shell command instead
- Skip Spotless formatting before committing
