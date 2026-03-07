# AI Agent Collaboration Guide

## Overview

This repository is configured with two AI coding assistant ecosystems working in parallel:
- **Claude Code** with Agent Teams (peer-to-peer collaboration)
- **Qwen Code** with SubAgents (hierarchical delegation)

Both systems have equivalent specialist agents covering the same expertise areas.

## Agent Specializations

Both Claude and Qwen have these specialized agents:

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

## Configuration

### Claude Code
- **Location**: `~/.claude/`
- **Settings**: `~/.claude/settings.json`
- **Agents**: `~/.claude/agents/*.md`
- **Features**:
  - Agent Teams enabled (experimental)
  - tmux split-pane mode
  - Permission mode: bypassPermissions
  - Pre-commit/pre-push hooks configured

### Qwen Code
- **Location**: `~/.qwen/`
- **Settings**: `~/.qwen/settings.json`
- **Agents**: `~/.qwen/agents/*.md`
- **Features**:
  - SubAgent delegation (automatic)
  - YOLO mode (auto-approve all)
  - Same pre-commit/pre-push hooks as Claude

## Multi-Agent Task Assignment

### Scenario: Full-Stack Feature with Security, Infrastructure, and Mobile

**Task**: Implement a new authentication system that needs:
- Backend API (OAuth2 + JWT)
- Frontend web UI
- Mobile apps (iOS + Android)
- Infrastructure setup (Kubernetes, secrets management)
- Security review

### Strategy 1: Claude Agent Teams (Parallel Collaboration)

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
- Each teammate works in parallel with own context
- Teammates message each other directly
- Shared task list coordinates work
- Split tmux panes show all progress simultaneously
- Mobile engineer can ask frontend about design patterns
- Backend can collaborate with security on JWT implementation
- Infrastructure coordinates with all on deployment requirements

### Strategy 2: Qwen SubAgents (Hierarchical Delegation)

```bash
qwen-code
```

Then ask:
```
I need to implement OAuth2 authentication across our full stack.

Requirements:
- Backend: Spring Boot OAuth2 Authorization Server with JWT
- Frontend: React login flow with token management
- Mobile: iOS and Android native auth with secure token storage
- Infrastructure: Kubernetes deployment with sealed secrets
- Security: OWASP compliance and vulnerability assessment

Please delegate to the appropriate subagents to:
1. Design the authentication architecture
2. Implement backend, frontend, and mobile components
3. Set up infrastructure
4. Perform security review
```

**How it works**:
- Qwen main agent orchestrates everything
- Automatically delegates to specialized subagents
- SubAgents report back to main agent
- Main agent synthesizes all work
- Automatic agent selection based on task

### Strategy 3: Hybrid Approach (Claude + Qwen in Parallel)

Use both simultaneously in different terminal sessions:

**Terminal 1 - Claude**:
```bash
claude
```
```
Create an agent team focused on implementation:
- backend-developer: Implement OAuth2 server and resource servers
- frontend-developer: Build web UI for authentication
- mobile-engineer: Implement mobile auth flows
```

**Terminal 2 - Qwen**:
```bash
qwen-code
```
```
Perform comprehensive review and architecture validation:
1. Security review of the authentication design (secops-engineer)
2. Architecture compliance check (architecture-guardian)
3. Infrastructure readiness assessment (infrastructure-engineer)
4. Performance and scalability analysis
```

**Benefits**:
- Claude team focuses on rapid implementation
- Qwen performs thorough review and validation
- Two independent perspectives catch more issues
- Parallel progress on implementation and review

## When to Use Which

### Use Claude Agent Teams When:
- ✅ Need peer-to-peer collaboration between agents
- ✅ Complex cross-domain tasks requiring discussion
- ✅ Agents need to challenge each other's approaches
- ✅ Want to see all work in parallel (tmux splits)
- ✅ Multiple independent modules being built simultaneously

### Use Qwen SubAgents When:
- ✅ Clear task delegation with focused specializations
- ✅ Main orchestrator coordinating all work
- ✅ Automatic agent selection preferred
- ✅ Single synthesized output desired
- ✅ Hierarchical workflow makes sense

### Use Both (Hybrid) When:
- ✅ Very complex, high-stakes projects
- ✅ Want implementation + independent review
- ✅ Need maximum code quality and coverage
- ✅ Multiple perspectives valuable
- ✅ Budget allows for dual AI usage

## Task Assignment Examples

### Example 1: Backend API + Frontend
**Claude**:
```
Create team: backend-developer and frontend-developer
Backend: Implement REST API with Spring Boot
Frontend: Build React UI consuming the API
Have them coordinate on API contract and error handling
```

### Example 2: Full Infrastructure Setup
**Qwen**:
```
Set up complete Kubernetes cluster with:
- Terraform for AWS infrastructure (infrastructure-engineer)
- Helm charts for application deployment (infrastructure-engineer)
- Monitoring stack (infrastructure-engineer)
- Security hardening (secops-engineer)
- Documentation (principal-engineer)
```

### Example 3: Mobile App with Backend
**Claude Team**:
```
Spawn:
- backend-developer: Build API
- mobile-engineer: iOS and Android apps
- identity-security-developer: Implement OAuth2
Let them collaborate on authentication flow and API design
```

### Example 4: Code Review
**Both**:
```
# Claude
Create review team to assess PR #123:
- secops-engineer: Security review
- backend-developer: Code quality review
- architecture-guardian: Architecture compliance

# Qwen (separate session)
Perform independent review of PR #123 focusing on:
- Performance implications
- Test coverage gaps
- Documentation completeness
```

## Quality Gates

Both Claude and Qwen are configured with the same git hooks:

**Pre-commit** (blocks on failure):
- Code formatting (mvn spotless:check)
- Unit tests (≥90% coverage required)
- Conventional Commits format validation

**Pre-push** (blocks on failure):
- Full test suite (mvn verify)
- SonarQube analysis (if SONAR_TOKEN set)
- Quality gate (≥90% coverage, no critical issues)

## Best Practices

1. **Start with Architecture**: Use principal-engineer or architecture-guardian first to design approach
2. **Security First**: Involve identity-security-developer and secops-engineer early
3. **Test Coverage**: Both systems enforce ≥90% unit and ≥80% integration tests
4. **Code Review**: Use both Claude teams and Qwen for independent reviews
5. **Documentation**: Let principal-engineer synthesize and document decisions
6. **Conventional Commits**: Both enforce conventional commits format

## Deployment

Ansible automatically deploys both configurations:

```bash
ansible-playbook playbook.yml -e setup_state=present --limit local
```

This installs:
- Claude Code agents to `~/.claude/agents/`
- Qwen Code agents to `~/.qwen/agents/`
- Settings for both with matching hooks
- Guides and documentation

## Troubleshooting

### Claude Agent Teams Not Working
- Ensure `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `~/.claude/settings.json`
- Verify tmux is installed: `which tmux`
- Check `teammateMode` is set to `"tmux"` or `"auto"`

### Qwen SubAgents Not Delegating
- Verify `tools.approvalMode` is `"yolo"` in `~/.qwen/settings.json`
- Check agents exist in `~/.qwen/agents/`
- Ensure agent markdown files have valid YAML frontmatter

### Permission Prompts
- Claude: `permissionMode: "bypassPermissions"` in settings.json
- Qwen: `tools.approvalMode: "yolo"` in settings.json

## Sources
- [Claude Code Agent Teams Documentation](https://code.claude.com/docs/en/agent-teams)
- [Qwen Code SubAgents Documentation](https://qwenlm.github.io/qwen-code-docs/en/users/features/sub-agents/)
- [Qwen Code Settings Reference](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/)
