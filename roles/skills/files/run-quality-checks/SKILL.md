---
name: run-quality-checks
description: Detect the build tool and run the full pre-commit quality gate — format, lint, test, SAST, and SCA.
---

# Run Quality Checks Skill

Run the full quality gate before committing. Detect the build tool, then execute checks in this order: format → lint → tests → SAST → SCA.

## Step 1 — Detect the build tool

```bash
ls pom.xml package.json pyproject.toml setup.py Pipfile 2>/dev/null
```

| File present | Build tool |
|---|---|
| `pom.xml` | Maven |
| `package.json` | npm / yarn / pnpm |
| `pyproject.toml` / `setup.py` / `Pipfile` | Python (uv / pip / Poetry) |

## Step 2 — Run quality checks

### Maven (Java / Kotlin)

```bash
mvn spotless:apply          # auto-format code
mvn checkstyle:check        # code style
mvn test                    # unit tests
mvn verify                  # unit + integration tests
mvn sonar:sonar             # SAST — SonarQube quality gate
mvn dependency-check:check  # SCA — OWASP CVE scan
```

If `mvn verify` fails, stop — do not proceed to SAST/SCA.

### npm / yarn / pnpm (JavaScript / TypeScript)

```bash
npm run format              # or: yarn format / pnpm format
npm run lint                # ESLint / Biome
npm test                    # unit tests
npm run build               # type-check + bundle
npm audit --audit-level=high  # SCA — npm audit
```

If no `format` script exists, try `npx prettier --write .`

### Python (uv / pip / Poetry)

```bash
uv run black .              # or: black .
uv run ruff check --fix .   # or: ruff check --fix .
uv run pytest               # unit tests
uv run bandit -r src/       # SAST
uv run pip-audit            # or: safety check — SCA
```

## Step 3 — Interpret results

| Tool | Failure condition | Action |
|------|------------------|--------|
| Format | Files changed | Review and stage the formatted changes |
| Lint | Any error | Fix all errors before proceeding |
| Tests | Any failure | Fix before committing |
| SAST | High/Critical finding | Fix before committing; document suppressed findings |
| SCA | CVSS ≥ 7 CVE | Upgrade dependency or document accepted risk |

## Safety rules

- Never use `--skip-tests`, `--no-verify`, or equivalent to bypass quality gates
- Never suppress SAST findings without a documented justification in the codebase
- Never accept a CVE with CVSS ≥ 7 without explicit sign-off
- If a check is not available (tool not installed), note it — do not silently skip
