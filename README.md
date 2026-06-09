# AI Agent Workforce

> Deploy Claude Code agent teams as code. Ansible automation for AI agent configurations, skills, and workspace management.

[![Build](https://github.com/muhamadto/ai-agent-workforce/actions/workflows/build.yml/badge.svg)](https://github.com/muhamadto/ai-agent-workforce/actions/workflows/build.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=muhamadto_ai-agent-workforce&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=muhamadto_ai-agent-workforce)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=muhamadto_ai-agent-workforce&metric=bugs)](https://sonarcloud.io/summary/new_code?id=muhamadto_ai-agent-workforce)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=muhamadto_ai-agent-workforce&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=muhamadto_ai-agent-workforce)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=muhamadto_ai-agent-workforce&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=muhamadto_ai-agent-workforce)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

AI Agent Workforce is an Ansible-based automation tool for deploying and managing Claude Code agent teams. It provides infrastructure-as-code for agent configurations, skills, and integrations.

### Key Features

- **Specialized Agents** - Pre-configured expert agents (backend, frontend, security, QA, BA, etc.)
- **Shared Skills** - Reusable slash-command skills deployed via symlink
- **Extensible Integrations** - MCP (Model Context Protocol) and custom plugins
- **Idempotent Operations** - Install and uninstall agents cleanly
- **Security-First** - Safe configuration management with environment-based secrets

## Quick Start

### Prerequisites

- macOS (Darwin)
- Ansible 2.9+
- Python 3.8+

## Installation

<details>
<summary>Expand</summary>

1. Clone the repository:

```bash
git clone https://github.com/muhamadto/ai-agent-workforce.git
cd ai-agent-workforce
```

2. Deploy all agents locally:

```bash
ansible-playbook playbook.yml -e setup_state=present --limit local
```

3. Deploy specific components using tags:

```bash
# Claude agents only
ansible-playbook playbook.yml -e setup_state=present --tags claude

# Skills only
ansible-playbook playbook.yml -e setup_state=present --tags skills
```

### Remote Deployment

Add remote hosts to `inventory.ini`:

```ini
[remote]
my-mac ansible_host=192.168.1.100 ansible_user=username
```

Deploy remotely:

```bash
ansible-playbook playbook.yml -e setup_state=present --limit remote --ask-become-pass
```

### Uninstallation

Remove all agents and configurations:

```bash
ansible-playbook playbook.yml -e setup_state=absent --limit local
```

</details>

## Architecture

### Project Structure

```
ai-agent-workforce/
├── playbook.yml              # Main orchestration playbook
├── inventory.ini             # Target hosts configuration
├── ansible.cfg               # Ansible settings
├── group_vars/
│   └── all.yml              # Global variables
└── roles/
    ├── claude/              # Claude Code agents
    └── skills/              # Shared skills
```

## Agent Teams

<details>
<summary>Expand</summary>

### Claude Code Agents

Located in `~/.claude/agents/`:
- **architecture-guardian** - Clean Architecture enforcer
- **backend-developer** - Java, Spring Boot, GraalVM expert
- **business-analyst** - Requirements elicitation, user stories, acceptance criteria
- **data-engineer** - ETL/ELT, big data expert
- **frontend-developer** - React, Next.js, Flutter expert
- **identity-security-developer** - OAuth2, OIDC, passkeys expert
- **infrastructure-engineer** - AWS, GCP, Kubernetes expert
- **mobile-engineer** - iOS, Android, cross-platform expert
- **principal-engineer** - Strategic decision-maker
- **qe-engineer** - Test strategy, automation, BDD, performance expert
- **secops-engineer** - OWASP, security tooling expert

### Shared Skills

Located in `~/.claude/skills/`:

| Skill | Description |
|---|---|
| `adr` | Create Architecture Decision Records with context, options, and rationale |
| `api-design` | Design and review API contracts (OpenAPI/REST/gRPC) for correctness, security, and business alignment |
| `db-migration-review` | Review database migrations for destructive ops, locks, and missing rollbacks |
| `dependency-review` | Evaluate dependency upgrades for breaking changes, CVEs, and license compliance |
| `git-branch` | Branch lifecycle — cut from `origin/main`, sync via rebase, never merge |
| `git-commit` | Conventional Commits compliant commit messages with hook awareness |
| `incident` | Incident response (detect → contain → resolve) and blameless postmortem |
| `release-notes` | Generate structured changelog from Conventional Commits between two refs |
| `run-quality-checks` | Full pre-commit quality gate — format, lint, test, SAST, SCA |
| `shortcut` | Shortcut project management via `short` CLI |
| `spike` | Time-boxed technical investigation with structured report and go/no-go outcome |
| `test-plan` | Structured test plans covering unit, integration, E2E, performance, and security |
| `threat-model` | STRIDE-based threat modelling for features and architecture changes |

</details>

## Configuration

<details>
<summary>Expand</summary>

### Variables

Edit `group_vars/all.yml` to customize:

```yaml
# Control installation state
setup_state: present  # or absent

# Model configuration (optional override)
# claude_default_model: "sonnet-4.5"
```

</details>

## Development

### Testing

```bash
# Syntax check
ansible-playbook playbook.yml --syntax-check

# Dry run
ansible-playbook playbook.yml --check

# Debug mode
ansible-playbook playbook.yml -vvvv
```

### Adding New Skills

<details>
<summary>Expand</summary>

1. Create the skill directory:

```bash
mkdir roles/skills/files/<skill-name>
```

2. Write `roles/skills/files/<skill-name>/SKILL.md` with a frontmatter header:

```markdown
---
name: skill-name
description: One-sentence description shown in the skills list.
---

# Skill Name

...
```

The skill is automatically picked up on the next playbook run — no task changes needed.

</details>

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting pull requests, reporting bugs, and adding new agents or skills.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## Roadmap

- [x] Skills framework support
- [ ] MCP server configurations
- [ ] Multi-platform support (Linux, WSL)
- [ ] Agent performance metrics
- [ ] CI/CD pipeline templates

## Support

- **Issues**: [GitHub Issues](https://github.com/muhamadto/ai-agent-workforce/issues)
- **Discussions**: [GitHub Discussions](https://github.com/muhamadto/ai-agent-workforce/discussions)
