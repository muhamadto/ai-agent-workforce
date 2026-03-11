---
name: release-notes
description: Generate structured release notes from git log between two refs, grouped by Conventional Commits type.
---

# Release Notes Skill

Generate structured, human-readable release notes from Conventional Commits history between two refs (tags, branches, or commits).

## When to use

- Cutting a release and need a changelog entry
- Generating sprint/milestone release notes
- Auditing what changed between two versions

---

## Step 1 — Identify the range

Determine the start and end refs:

```bash
# Latest tag (previous release)
git describe --tags --abbrev=0

# All tags, sorted by version
git tag --sort=-version:refname | head -10
```

Typical range: `<previous-tag>..HEAD` or `<previous-tag>..<new-tag>`.

## Step 2 — Extract commits in range

```bash
git log <previous-tag>..HEAD \
  --pretty=format:"%H %s" \
  --no-merges
```

Filter out non-conventional commits (chore, ci, docs) if they are not user-facing:

```bash
git log <previous-tag>..HEAD \
  --pretty=format:"%H %s" \
  --no-merges \
  | grep -E '^[a-f0-9]+ (feat|fix|perf|refactor|revert)[(!:]'
```

## Step 3 — Group by type

Organise commits into sections. Use this structure:

```markdown
## [<version>] — YYYY-MM-DD

### Breaking Changes

- feat(auth)!: change token format — existing sessions will be invalidated

### Features

- feat(payments): add Apple Pay support (#142)
- feat(api): expose batch endpoint for bulk updates (#138)

### Bug Fixes

- fix(auth): prevent token refresh race condition (#145)
- fix(api): return 422 instead of 500 on validation error (#140)

### Performance

- perf(db): add composite index on orders table (#139)

### Deprecations

- refactor(api): mark v1 endpoints as deprecated — remove in v3.0
```

**Section order:** Breaking Changes → Features → Bug Fixes → Performance → Deprecations → Other

## Step 4 — Extract PR/issue references

Append issue/PR numbers from commit footers or message bodies:

```bash
git log <previous-tag>..HEAD \
  --pretty=format:"%s %b" \
  --no-merges \
  | grep -oE "(Closes|Fixes|Resolves) #[0-9]+" | sort -u
```

Link them in the notes: `(#123)` where 123 is the PR or issue number.

## Step 5 — Write the release notes file

Prepend to `CHANGELOG.md` (create if absent):

```bash
# Verify CHANGELOG.md exists
find . -maxdepth 2 -name "CHANGELOG.md" 2>/dev/null | head -3
```

Format for `CHANGELOG.md`:

```markdown
# Changelog

All notable changes are grouped by Conventional Commits type.

## [Unreleased]

## [<version>] — YYYY-MM-DD
...
```

## Step 6 — Commit using the git-commit skill

Use the [/git-commit](../git-commit/SKILL.md) skill:

```text
docs(changelog): add release notes for v<version>
```

---

## Conventional Commits → section mapping

| Prefix | Section |
|--------|---------|
| `feat!` / `BREAKING CHANGE` | Breaking Changes |
| `feat` | Features |
| `fix` | Bug Fixes |
| `perf` | Performance |
| `refactor` | Other (include if user-visible) |
| `revert` | Bug Fixes |
| `docs`, `chore`, `ci`, `build`, `test` | Omit (internal) |

---

## Safety rules

- Never delete entries from `CHANGELOG.md` — only prepend
- Always include the date in ISO format (`YYYY-MM-DD`)
- Breaking changes MUST appear at the top of the release section
- Do not include commit hashes in the published notes — use PR/issue numbers
- If the range is ambiguous, confirm with the user before generating
