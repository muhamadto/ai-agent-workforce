---
name: dependency-review
description: Review dependency upgrades for breaking changes, CVEs, license compatibility, and bundle size impact before merging.
---

# Dependency Review Skill

Evaluate dependency upgrades before merging: breaking changes, security vulnerabilities, license compliance, and runtime impact.

## When to use

- A PR bumps one or more dependencies
- Running a scheduled dependency audit
- Evaluating whether to adopt a new library

---

## Step 1 — Identify changed dependencies

Use the merge base so the full branch diff is covered, not just the last commit:

```bash
BASE=$(git merge-base HEAD origin/main)

# Maven
git diff "$BASE"..HEAD pom.xml | grep "^\+" | grep -E "<version>|<artifactId>"

# npm / yarn / pnpm
git diff "$BASE"..HEAD package.json package-lock.json yarn.lock | grep "^\+" | grep -E '"version":|resolved'

# Python
git diff "$BASE"..HEAD requirements*.txt pyproject.toml uv.lock | grep "^\+"
```

List every dependency that changed, with old → new version.

## Step 2 — Check for breaking changes

### Maven

```bash
# Check the changelog / GitHub releases for the dependency
# Look for BREAKING CHANGE or migration guide in the release notes
```

For each major version bump (`X.y.z` → `(X+1).y.z`):
- Read the release notes between the old and new version
- Search for `breaking`, `removed`, `deprecated`, `migration`
- Check if the public API your code uses has changed

### npm / pnpm

```bash
npm outdated                         # see what is outdated
npx npm-check-updates --interactive  # review each upgrade
```

For major version bumps, check the package's `CHANGELOG.md` or GitHub releases.

### Python

```bash
uv pip list --outdated     # or: pip list --outdated
```

---

## Step 3 — Security scan

Run the appropriate SCA tool for the stack:

```bash
# Maven
mvn dependency-check:check

# npm
npm audit --audit-level=high

# Python
uv run pip-audit   # or: safety check
```

For each finding:

| CVSS Score | Action |
|------------|--------|
| 9.0 – 10.0 (Critical) | Block — must upgrade or remove |
| 7.0 – 8.9 (High) | Block — must upgrade or accept with documented sign-off |
| 4.0 – 6.9 (Medium) | Upgrade preferred — document if deferred |
| 0.1 – 3.9 (Low) | Note — address in next scheduled audit |

## Step 4 — License check

```bash
# Maven
mvn license:check                     # enforce approved licenses

# npm
npx license-checker --onlyAllow "MIT;ISC;Apache-2.0;BSD-2-Clause;BSD-3-Clause"

# Python
uv run pip-licenses --format=table
```

**Approved licenses:** MIT, Apache-2.0, ISC, BSD-2-Clause, BSD-3-Clause, MPL-2.0

**Flag for legal review:** GPL, LGPL, AGPL, SSPL, Commons Clause, proprietary

---

## Step 5 — Impact assessment

### Runtime / startup impact

For backend (JVM):
```bash
# Compare startup time and heap usage before and after upgrade
# Check if the new version adds heavy transitive dependencies
mvn dependency:tree -Dincludes=<groupId>:<artifactId>
```

For frontend (JS):
```bash
# Check bundle size impact
npx bundlephobia <package>@<new-version>
```

### API compatibility

```bash
# JVM (Java / Kotlin)
grep -r "<dependency-name>" . --include="*.java" --include="*.kt" | head -20

# Node / npm (JS / TS)
grep -r "<dependency-name>" . --include="*.js" --include="*.ts" \
  --include="*.jsx" --include="*.tsx" | head -20

# Python
grep -r "<dependency-name>" . --include="*.py" | head -20
```

Review usages for any deprecated or removed APIs.

---

## Step 6 — Output the review

```text
## Dependency Review

### Changed Dependencies

| Dependency | Old | New | Type |
|------------|-----|-----|------|
| spring-boot | 3.3.0 | 3.4.1 | Minor |
| jackson-databind | 2.16.0 | 2.17.0 | Minor |
| lodash | 4.17.19 | 4.17.21 | Patch |

### Breaking Changes

- **spring-boot 3.4.x**: <describe any breaking change and migration steps>

### Security Findings

| CVE | Package | CVSS | Status |
|-----|---------|------|--------|
| CVE-2024-XXXXX | jackson-databind 2.16.0 | 8.1 (High) | Fixed in 2.17.0 — upgrade approved |

### License Changes

- No new licenses introduced

### Recommendation

✅ Approve / ⚠️ Approve with conditions / ❌ Block

<Rationale>
```

---

## Safety rules

- Never approve a dependency with an unresolved Critical CVE
- Never accept a GPL/AGPL dependency in a proprietary codebase without legal sign-off
- Always check transitive dependencies for new CVEs — not just direct dependencies
- Pin patch versions in production — never use `*` or `latest` in lockfiles
- If the upgrade is a major version, require a smoke test in staging before merging
