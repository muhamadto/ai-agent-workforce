[//]: # (Licensed to Muhammad Hamadto 2026)
[//]: # (Licensed under the Apache License, Version 2.0)

# AI Collaboration Guide

## Overview

This repository deploys Claude Code with specialized Agent Teams for peer-to-peer collaboration across engineering disciplines.

## Agent Specializations

| Agent | Expertise |
|-------|-----------|
| **backend-developer** | Java 24+, Spring Boot 4.x, Spring Native, GraalVM, Clean Architecture |
| **frontend-developer** | React 18+, Next.js 14+, Flutter 3.x, responsive UI |
| **mobile-engineer** | iOS (Swift), Android (Kotlin), Flutter, React Native |
| **infrastructure-engineer** | AWS, GCP, Kubernetes, Terraform, private cloud |
| **identity-security-developer** | OAuth2, OIDC, passkeys, Spring Security |
| **data-engineer** | ETL/ELT, big data, SQL optimization, Python |
| **secops-engineer** | OWASP, security tooling, vulnerability analysis |
| **architecture-guardian** | Clean Architecture enforcement, SOLID principles |
| **principal-engineer** | Strategic decisions, conflict resolution |
| **business-analyst** | Requirements elicitation, user stories, acceptance criteria |
| **qe-engineer** | Test strategy, BDD, automation, performance testing |

## Configuration

- **Location**: `~/.claude/`
- **Settings**: `~/.claude/settings.json`
- **Agents**: `~/.claude/agents/*.md`
- **Skills**: `~/.claude/skills/` (symlink to `~/.skills/`)
- **Features**:
  - Agent Teams enabled (experimental)
  - tmux split-pane mode
  - Permission mode: bypassPermissions
  - Pre-commit/pre-push hooks configured

## Multi-Agent Task Assignment

### Example: Full-Stack Feature with Security, Infrastructure, and Mobile

**Task**: Implement a new authentication system that needs:
- Backend API (OAuth2 + JWT)
- Frontend web UI
- Mobile apps (iOS + Android)
- Infrastructure setup (Kubernetes, secrets management)
- Security review

```bash
claude
```

Then ask:
```
Create an agent team for implementing OAuth2 authentication:

1. Spawn identity-security-developer to design the OAuth2 flow and JWT strategy
2. Spawn backend-developer to implement the API with Spring Security
3. Spawn frontend-developer to build the login UI with React
4. Spawn mobile-engineer to implement authentication in mobile apps
5. Spawn infrastructure-engineer to set up Kubernetes secrets and ingress
6. Spawn secops-engineer to perform security review

Have them collaborate directly, share findings, and coordinate dependencies.
Use plan mode for identity-security-developer to review the approach first.
```

**How it works**:
- Each teammate works in parallel with its own context
- Teammates message each other directly
- Shared task list coordinates work
- Split tmux panes show all progress simultaneously

## Task Assignment Examples

### Example 1: Backend API + Frontend
```
Create team: backend-developer and frontend-developer
Backend: Implement REST API with Spring Boot
Frontend: Build React UI consuming the API
Have them coordinate on API contract and error handling
```

### Example 2: Full Infrastructure Setup
```
Create team:
- infrastructure-engineer: Terraform AWS infra, Helm charts, monitoring stack
- secops-engineer: Security hardening
- principal-engineer: Documentation
```

### Example 3: Mobile App with Backend
```
Spawn:
- backend-developer: Build API
- mobile-engineer: iOS and Android apps
- identity-security-developer: Implement OAuth2
Let them collaborate on authentication flow and API design
```

### Example 4: Code Review
```
Create review team to assess PR #123:
- secops-engineer: Security review
- backend-developer: Code quality review
- architecture-guardian: Architecture compliance
```

## Quality Gates

**Pre-commit** (blocks on failure):
- Code formatting (mvn spotless:check)
- Unit tests (≥90% coverage required)
- Conventional Commits format validation

**Pre-push** (blocks on failure):
- Full test suite (mvn verify)
- SonarQube analysis (if SONAR_TOKEN set)
- Quality gate (≥90% coverage, no critical issues)

## Best Practices

1. **Start with Architecture**: Use `principal-engineer` or `architecture-guardian` first to design the approach
2. **Security First**: Involve `identity-security-developer` and `secops-engineer` early
3. **Test Coverage**: Enforce ≥90% unit and ≥80% integration tests
4. **Conventional Commits**: All hooks enforce the conventional commits format

## Deployment

```bash
ansible-playbook playbook.yml -e setup_state=present --limit local
```

This installs:
- Claude Code agents to `~/.claude/agents/`
- Settings with matching hooks
- Skills symlinked to `~/.claude/skills/`

## Troubleshooting

### Agent Teams Not Working
- Ensure agent teams experimental flag is enabled in `~/.claude/settings.json`
- Verify tmux is installed: `which tmux`
- Check `teammateMode` is set to `"tmux"` or `"auto"`

### Permission Prompts
- Claude: `permissionMode: "bypassPermissions"` in settings.json

## Sources
- [Claude Code Agent Teams Documentation](https://code.claude.com/docs/en/agent-teams)
