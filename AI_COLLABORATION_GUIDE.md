# AI Agent Collaboration Guide

## Overview

This repository is configured with three AI coding assistant ecosystems working in parallel:
- **Claude Code** with Agent Teams (peer-to-peer collaboration)
- **Qwen Code** with SubAgents (hierarchical delegation)
- **Gemini CLI** with Repo-Navigation-First agents (explore-then-implement)

All three systems have equivalent specialist agents covering the same expertise areas.

## Agent Specializations

All three models have these specialized agents:

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

## Model Comparison

| Model | Strength | Agent Style | Best For |
|-------|----------|-------------|----------|
| **Claude** | Long-context behavioral adherence | Constitution — verbose doctrine, philosophy, rulebooks | Architecture reviews, security, complex cross-cutting decisions |
| **Qwen Coder** | Token-efficient instruction following | Compressed rules — short, direct, structured | Fast implementation, repetitive coding tasks, strict rule execution |
| **Gemini** | Tool orchestration, repo navigation, large-context reasoning | Playbook — tool-aware, explore-first, task-focused | Codebase discovery, multi-file refactors, planning across a large repo |

## Recommended Model per Agent

| Agent | Best Model | Reasoning |
|-------|------------|-----------|
| **architecture-guardian** | Claude | Doctrine-holding + judgment. Claude's core strength. |
| **backend-developer** | Claude or Qwen | Claude for complex domain logic. Qwen for CRUD, boilerplate, speed. |
| **frontend-developer** | Claude or Qwen | Claude for state management complexity. Qwen for component boilerplate. |
| **data-engineer** | Gemini or Claude | Gemini for tracing lineage. Claude for complex transformations. |
| **identity-security-developer** | Claude | Non-negotiable. You want the model that won't drift from security doctrine. |
| **infrastructure-engineer** | Gemini or Claude | Gemini for exploration and blast-radius mapping. Claude for complex IaC. |
| **mobile-engineer** | Claude or Qwen | Claude for complex patterns. Qwen for standard screens and boilerplate. |
| **principal-engineer** | Claude | Trade-off analysis and ADRs are Claude's native mode. |
| **secops-engineer** | Claude (judge) + Gemini (scan) | Hybrid: Gemini scans and discovers, Claude judges against standards. |

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
- **Style**: Constitution-based — reads doctrine, judges against rules

### Qwen Code
- **Location**: `~/.qwen/`
- **Settings**: `~/.qwen/settings.json`
- **Agents**: `~/.qwen/agents/*.md`
- **Features**:
  - SubAgent delegation (automatic)
  - YOLO mode (auto-approve all)
  - Same pre-commit/pre-push hooks as Claude
- **Style**: Compressed rules — token-efficient, fast implementation

### Gemini CLI
- **Location**: `~/.gemini/`
- **Settings**: `~/.gemini/settings.json`
- **Agents**: `~/.gemini/agents/*.md`
- **Features**:
  - Repo-navigation-first approach
  - Tool-aware agents (read_file, glob, grep, run_shell_command)
  - Role-specific attention cones
  - Constraint checkpoints mid-workflow
  - Model: gemini-2.5-pro
- **Style**: Playbook-based — explores first, then implements

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

### Strategy 3: Gemini CLI (Repo-Navigation-First)

```bash
gemini
```

Then ask:
```
@backend-developer Implement OAuth2 authentication with Spring Boot.

First, explore the codebase:
1. Map the existing service structure
2. Find similar authentication patterns already in use
3. Read the closest existing use case before implementing

Then implement following Clean Architecture layers.
```

**How it works**:
- Agent explores repo before implementing (shell commands, grep, glob)
- Reads existing patterns before writing new code
- Constraint checkpoints mid-workflow (e.g., "which layer does this belong in?")
- Uses gemini-2.5-pro for large-context reasoning
- Tool-aware: runs diagnostic commands, maps dependencies

### Strategy 4: Hybrid Approach (All Three Models)

Use all three simultaneously for maximum coverage:

**Terminal 1 - Claude (Architecture + Security)**:
```bash
claude
```
```
@principal-engineer @identity-security-developer
Design the OAuth2 architecture and security model.
Write ADRs for key decisions.
```

**Terminal 2 - Qwen (Implementation)**:
```bash
qwen-code
```
```
Implement the OAuth2 server based on the ADRs.
Generate unit tests with ≥90% coverage.
```

**Terminal 3 - Gemini (Discovery + Validation)**:
```bash
gemini
```
```
@architecture-guardian @secops-engineer
1. Map the dependency graph of the OAuth2 implementation
2. Find any security vulnerabilities or architecture violations
3. Report violations with file paths and line numbers
```

**Benefits**:
- Claude: Holds doctrine, makes trade-off decisions
- Qwen: Fast, token-efficient implementation
- Gemini: Explores, discovers issues, validates against actual code

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
- ✅ Architecture reviews and security doctrine enforcement

### Use Qwen SubAgents When:
- ✅ Clear task delegation with focused specializations
- ✅ Main orchestrator coordinating all work
- ✅ Automatic agent selection preferred
- ✅ Single synthesized output desired
- ✅ Hierarchical workflow makes sense
- ✅ Fast implementation of repetitive patterns (CRUD, boilerplate)

### Use Gemini CLI When:
- ✅ Unfamiliar codebase requiring exploration
- ✅ Multi-file refactors across layers
- ✅ Need to trace dependencies or data lineage
- ✅ Tool orchestration (grep, git, find, shell commands)
- ✅ Large-context reasoning across the entire repo
- ✅ Validation against actual code (not just doctrine)

### Use All Three (Hybrid) When:
- ✅ Very complex, high-stakes projects
- ✅ Want implementation + independent review + validation
- ✅ Need maximum code quality and coverage
- ✅ Multiple perspectives valuable
- ✅ Budget allows for triple AI usage

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
3. **Test Coverage**: All three systems enforce ≥90% unit and ≥80% integration tests
4. **Code Review**: Use Claude, Qwen, and Gemini for independent reviews
5. **Documentation**: Let principal-engineer synthesize and document decisions
6. **Conventional Commits**: All three enforce conventional commits format
7. **Model Selection**: Match the model to the task (see Recommended Model per Agent table)

## Deployment

Ansible automatically deploys all three configurations:

```bash
ansible-playbook playbook.yml -e setup_state=present --limit local
```

This installs:
- Claude Code agents to `~/.claude/agents/`
- Qwen Code agents to `~/.qwen/agents/`
- Gemini CLI agents to `~/.gemini/agents/`
- Settings for all three with matching hooks
- Guides and documentation

## Troubleshooting

### Claude Agent Teams Not Working
- Ensure agent teams experimental flag is enabled in `~/.claude/settings.json`
- Verify tmux is installed: `which tmux`
- Check `teammateMode` is set to `"tmux"` or `"auto"`

### Qwen SubAgents Not Delegating
- Verify `tools.approvalMode` is `"yolo"` in `~/.qwen/settings.json`
- Check agents exist in `~/.qwen/agents/`
- Ensure agent markdown files have valid YAML frontmatter

### Gemini CLI Agents Not Exploring
- Check agents exist in `~/.gemini/agents/`
- Verify agent files have proper YAML frontmatter (name, description, tools)
- Ensure `gemini-2.5-pro` model is selected in settings.json
- Agents should have `run_shell_command` in tools list for exploration

### Permission Prompts
- Claude: `permissionMode: "bypassPermissions"` in settings.json
- Qwen: `tools.approvalMode: "yolo"` in settings.json

## Sources
- [Claude Code Agent Teams Documentation](https://code.claude.com/docs/en/agent-teams)
- [Qwen Code SubAgents Documentation](https://qwenlm.github.io/qwen-code-docs/en/users/features/sub-agents/)
- [Qwen Code Settings Reference](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/)
- [Gemini CLI Sub-Agents Documentation](https://qwenlm.github.io/qwen-code-docs/en/users/features/sub-agents/)
