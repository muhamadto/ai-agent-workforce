# Conventional Commits Standard

**ALL agents MUST use Conventional Commits format for ALL git commit messages.**

## Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Types (REQUIRED)

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (white-space, formatting, missing semi-colons, etc)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies (Maven, npm, Docker)
- **ci**: Changes to CI configuration files and scripts (GitHub Actions, Jenkins)
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

## Scope (OPTIONAL)

- Component or module name affected (e.g., `auth`, `api`, `database`, `ui`)
- Examples: `feat(auth):`, `fix(api):`, `refactor(database):`

## Description (REQUIRED)

- Use imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize first letter
- No period (.) at the end
- Max 72 characters

## Body (OPTIONAL)

- Use imperative, present tense
- Include motivation for the change
- Contrast with previous behavior

## Footer (OPTIONAL)

- Reference issues: `Closes #123`, `Fixes #456`
- Breaking changes: `BREAKING CHANGE: <description>`

## Examples

### Simple feature:
```
feat: add user authentication with OAuth2

Implemented OAuth2 authorization code flow with PKCE for secure user login.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Bug fix with scope:
```
fix(api): prevent race condition in token refresh

Add mutex lock to prevent concurrent token refresh requests that could cause
duplicate refresh token usage and authentication failures.

Fixes #234

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Breaking change:
```
feat(auth)!: change password hashing to Argon2id

BREAKING CHANGE: Existing password hashes (BCrypt) will need to be migrated.
Users will need to reset passwords on next login.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Refactoring:
```
refactor(backend): extract repository interfaces to domain layer

Move repository interfaces from infrastructure to domain layer to comply with
Clean Architecture dependency rule. Implementations remain in infrastructure.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Documentation:
```
docs: add API authentication guide

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Testing:
```
test(api): add integration tests for user registration

Add comprehensive integration tests covering successful registration,
validation errors, duplicate email handling, and password strength requirements.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### CI/CD:
```
ci: add SonarQube quality gate to pipeline

Fail build if code coverage < 80% or any critical security issues detected.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

## Validation Rules

1. ✅ Type is REQUIRED and must be one of the standard types
2. ✅ Colon after type/scope is REQUIRED
3. ✅ Space after colon is REQUIRED
4. ✅ Description is REQUIRED
5. ✅ Description must be lowercase (except proper nouns)
6. ✅ Description must not end with period
7. ✅ Description max 72 characters
8. ✅ Breaking changes must include `BREAKING CHANGE:` in footer or `!` after type/scope
9. ✅ Co-Authored-By line is REQUIRED for agent commits

## DO NOT

❌ `Add feature` - missing type
❌ `feat:add feature` - missing space after colon
❌ `feat: Add feature` - description starts with capital letter
❌ `feat: add feature.` - description ends with period
❌ `added feature` - wrong tense (use imperative: "add" not "added")
❌ `feat: adding feature` - wrong tense (use "add" not "adding")

## Tools

Optional: Use commitlint for automated validation
```bash
npm install -g @commitlint/cli @commitlint/config-conventional
```