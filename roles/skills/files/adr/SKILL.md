---
name: adr
description: Create an Architecture Decision Record (ADR) to document a significant architectural decision, its context, options considered, and rationale.
---

# ADR Skill

Document architectural decisions in a lightweight, durable format. ADRs record the context, options, decision, and consequences so future team members understand why the architecture is the way it is.

## When to use

- A significant technology choice is being made (framework, database, messaging system, auth approach)
- A design trade-off has been resolved and the reasoning should be preserved
- A pattern or convention is being established for the team
- A previous decision is being superseded or reversed

---

## Step 1 — Find the ADR directory

```bash
ADR_DIR=$(find . -type d \( -name "adr" -o -name "decisions" \) \
  | grep -v node_modules | head -1)
echo "ADR directory: ${ADR_DIR:-docs/adr (will be created)}"
```

Common locations: `docs/adr/`, `doc/adr/`, `architecture/decisions/`. If none is found, default to `docs/adr/` and create it. Use this resolved path in all subsequent steps — do not hardcode `docs/adr/`.

## Step 2 — Determine the next ADR number

```bash
ls "${ADR_DIR}"/*.md 2>/dev/null | sort | tail -1
```

ADR filenames follow the pattern `NNNN-<title>.md` (e.g. `0001-use-postgresql.md`). Increment the highest number.

## Step 3 — Write the ADR

Create `<adr-dir>/NNNN-<kebab-case-title>.md`:

```markdown
# ADR-NNNN: <Title>

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded by [ADR-XXXX](XXXX-<title>.md)
**Deciders:** <names or roles>

---

## Context

<Describe the situation, forces, and constraints that make this decision necessary.
Include relevant technical and business drivers. What problem are we solving?>

## Decision Drivers

- <driver 1>
- <driver 2>

## Options Considered

### Option 1: <name>

**Pros:**
- <pro>

**Cons:**
- <con>

### Option 2: <name>

**Pros:**
- <pro>

**Cons:**
- <con>

## Decision

We will use **<chosen option>**.

<Explain the rationale. Why does this option best satisfy the decision drivers?>

## Consequences

### Positive
- <expected benefit>

### Negative
- <known trade-off or cost>

### Risks
- <risk and mitigation>

## Links

- Supersedes: [ADR-XXXX](XXXX-<title>.md) *(if applicable)*
- Superseded by: *(leave blank until superseded)*
- Related: <link to RFC, issue, or PR>
```

## Step 4 — Update ADR index (if one exists)

```bash
find "${ADR_DIR}" -name "README.md" -o -name "index.md" 2>/dev/null | head -1
```

If an index exists, append the new entry. If not, create `<adr-dir>/README.md`:

```markdown
# Architecture Decision Records

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0001](0001-<title>.md) | <Title> | Accepted |
```

## Step 5 — Commit using the git-commit skill

Use the [/git-commit](../git-commit/SKILL.md) skill. Commit message format:

```text
docs(adr): add ADR-NNNN <title>

<one-line summary of the decision>
```

---

## Status lifecycle

| Status | Meaning |
|--------|---------|
| `Proposed` | Under discussion — not yet decided |
| `Accepted` | Decision made and active |
| `Deprecated` | No longer relevant; context has changed |
| `Superseded by ADR-XXXX` | Replaced by a newer decision |

When superseding a decision, update the old ADR's status to `Superseded by [ADR-XXXX](...)` and link back.

---

## Safety rules

- Never delete an ADR — mark it `Deprecated` or `Superseded`
- Never edit an accepted ADR's decision retroactively — create a new ADR instead
- Always record the date and deciders
- Keep ADRs short — if it needs more than two pages, split context into a separate design doc
