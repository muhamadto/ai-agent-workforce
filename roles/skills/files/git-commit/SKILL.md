---
name: git-commit
description: Stage changes and create a Conventional Commits compliant commit message, respecting any active git hooks.
---

# Git Commit Skill

Analyse staged (or unstaged) changes, craft a Conventional Commits message, and commit — respecting whatever hooks are active in this repository.

## Step 1 — Discover active hooks

```bash
git config core.hooksPath
```text

This resolves across all git config scopes (local → global → system) and returns the active path. Two outcomes:

- **Returns a path** → Git loads hooks exclusively from that directory. `.git/hooks/` is completely ignored.
- **Returns nothing** → Git uses `.git/hooks/` (the built-in default).

List whichever applies to see which hooks will run:

```bash
ls -1 "$(git config core.hooksPath 2>/dev/null || echo .git/hooks)"
```text

The following hook names are supported by Git at `~/.git-hooks/` (or any `core.hooksPath` directory):

| Hook | Trigger |
|------|---------|
| `pre-commit` | Before the commit is created — used for linting, tests, formatting |
| `commit-msg` | After message is written — used for format validation |
| `prepare-commit-msg` | Before the editor opens — used for message templating |
| `post-commit` | After commit is created — used for notifications |
| `pre-push` | Before push to remote — used for quality gates |
| `post-merge` | After a merge — used for dependency updates |
| `post-checkout` | After branch switch — used for environment setup |
| `pre-rebase` | Before rebase — used for safety checks |
| `pre-applypatch` | Before patch is applied — used for patch validation |

## Step 2 — Check staged changes

```bash
git status
git diff --staged
```text

If nothing is staged, check unstaged changes:

```bash
git diff
```text

Stage what is appropriate before committing. Never use `git add -A` or `git add .` blindly — stage specific files to avoid accidentally including secrets or unrelated changes.

## Step 3 — Craft the commit message

Follow Conventional Commits format strictly:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

Signed-off-by: <git config user.name> <git config user.email>
```text

### Types

| Type | Use when |
|------|----------|
| `feat` | Adding a new feature |
| `fix` | Fixing a bug |
| `docs` | Documentation only |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code restructure — no feature or bug fix |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `build` | Build system or dependency changes |
| `ci` | CI/CD configuration changes |
| `chore` | Maintenance — no src or test change |
| `revert` | Reverting a previous commit |

### Rules

1. Type is REQUIRED and must be one of the standard types above
2. Colon after type/scope is REQUIRED
3. Space after colon is REQUIRED
4. Description is REQUIRED — imperative mood, lowercase, no period, max 72 characters
5. Scope is optional — a noun in parentheses, lowercase component name e.g. `feat(auth):`, `fix(api):`
6. If a body is included, a blank line MUST separate the subject from the body
7. Breaking change: append `!` after type/scope OR add `BREAKING CHANGE:` footer
8. Issue references go in footer: `Closes #123`, `Fixes #456`
9. `Signed-off-by` is REQUIRED on every commit — must be preceded by an empty line, exactly as shown in the examples above
10. Agent commits: must NOT include `Co-Authored-By:` footer

### Body (optional)

- Use imperative, present tense
- Explain the motivation for the change
- Contrast with the previous behaviour

### Valid examples

Simple feature:
```text
feat(auth): add OAuth2 login with PKCE

Implemented OAuth2 authorization code flow with PKCE for secure user login.

Signed-off-by: muhamadto <github.stencil525@passmail.net>
```text

Bug fix with issue reference:
```text
fix(api): prevent race condition in token refresh

Add mutex lock to prevent concurrent token refresh requests that could cause
duplicate refresh token usage and authentication failures.

Fixes #234

Signed-off-by: muhamadto <github.stencil525@passmail.net>
```text

Breaking change:
```text
feat(auth)!: change password hashing to Argon2id

BREAKING CHANGE: existing BCrypt hashes must be migrated — users will need
to reset passwords on next login.

Signed-off-by: muhamadto <github.stencil525@passmail.net>
```text

Refactoring:
```text
refactor(backend): extract repository interfaces to domain layer

Move repository interfaces from infrastructure to domain layer to comply with
Clean Architecture dependency rule. Implementations remain in infrastructure.

Signed-off-by: muhamadto <github.stencil525@passmail.net>
```text

Tests:
```text
test(api): add integration tests for user registration

Add comprehensive integration tests covering successful registration,
validation errors, duplicate email handling, and password strength requirements.

Signed-off-by: muhamadto <github.stencil525@passmail.net>
```text

Documentation:
```text
docs: update authentication guide

Signed-off-by: muhamadto <github.stencil525@passmail.net>
```text

CI/CD:
```text
ci: add SonarQube quality gate to pipeline

Fail build if code coverage < 80% or any critical security issues detected.

Signed-off-by: muhamadto <github.stencil525@passmail.net>
```text

### Invalid — do not use

```text
Add OAuth2           ← missing type
feat:add feature     ← missing space after colon
feat: Add feature    ← uppercase description
feat: add feature.   ← period at end
added feature        ← wrong tense — use imperative ("add" not "added")
feat: adding feature ← wrong tense — use imperative ("add" not "adding")
```text

Missing blank line between subject and body:
```text
feat: add new feature
This body follows directly — blank line required above it

Signed-off-by: muhamadto <github.stencil525@passmail.net>
```text

## Step 4 — Resolve committer identity

Read name and email from git config — this works on all platforms (macOS, Linux, Windows):

```bash
git config user.name
git config user.email
```text

These resolve across local → global → system scope, same as any git config value. Use the output to construct the `Signed-off-by` footer:

```text
Signed-off-by: <user.name> <user.email>
```text

Example: if `user.name = muhamadto` and `user.email = github.stencil525@passmail.net`, the footer is:

```text
Signed-off-by: muhamadto <github.stencil525@passmail.net>
```text

## Step 5 — Commit

Always pass the message via heredoc to preserve formatting:

```bash
git commit -m "$(cat <<'EOF'
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

Signed-off-by: <user.name> <user.email>
EOF
)"
```text

> **Note:** On Windows (no heredoc support), use `-m` with `\n` newlines via PowerShell:
> ```powershell
> git commit -m "<type>: <description>`n`nSigned-off-by: <user.name> <user.email>"
> ```

## Step 6 — Handle hook failures

If a hook fails, **do not retry the same commit** and do not use `--no-verify` unless explicitly asked.

Instead:
1. Read the hook output carefully — it will tell you what failed
2. Fix the root cause (formatting, test failure, message format, etc.)
3. Re-stage if needed
4. Commit again as a new attempt

To identify which hook failed:

```bash
# Check what hooks are active
ls -la <hooks-path>/

# Read the failing hook to understand what it checks
cat <hooks-path>/pre-commit
```text

## Safety rules

- Never run `git config --global` changes
- Never use `--no-verify` unless the user explicitly asks
- Never force-push (`--force`) unless the user explicitly asks
- Never commit files that may contain secrets (`.env`, credential files, private keys)
- Warn the user if they request any of the above
