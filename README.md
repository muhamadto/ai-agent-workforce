# AI Agent Workforce

> Deploy AI agent teams as code. Ansible automation for multi-model AI agents with pluggable integrations, task orchestration, and workspace management.

[![Build](https://github.com/muhamadto/ai-agent-workforce/actions/workflows/build.yml/badge.svg)](https://github.com/muhamadto/ai-agent-workforce/actions/workflows/build.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=muhamadto_ai-agent-workforce&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=muhamadto_ai-agent-workforce)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=muhamadto_ai-agent-workforce&metric=bugs)](https://sonarcloud.io/summary/new_code?id=muhamadto_ai-agent-workforce)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=muhamadto_ai-agent-workforce&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=muhamadto_ai-agent-workforce)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=muhamadto_ai-agent-workforce&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=muhamadto_ai-agent-workforce)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

AI Agent Workforce is an Ansible-based automation tool for deploying and managing AI agent teams across multiple models and platforms. It provides infrastructure-as-code for AI development environments, agent configurations, and task orchestration tools.

### Supported AI Models

- **Claude Code** - Anthropic's Claude with specialized agent teams
- **Qwen Code** - Alibaba's Qwen with YOLO-mode agent configurations
- **Gemini CLI** - Google's Gemini with repo-navigation-first agents

#### What Each Model Is Good At

| Model | Strength | Agent Style | Best For | When to Use |
|---|---|---|---|---|
| **Claude** | Long-context behavioral adherence | Constitution — verbose doctrine, philosophy, rulebooks | Architecture reviews, security, complex cross-cutting decisions | Default for anything non-trivial. Best balance of reasoning + implementation. Use when quality > speed, or when Claude Code rate limits hit and you need a fallback. |
| **Qwen Coder** | Token-efficient instruction following | Compressed rules — short, direct, structured | Fast implementation, repetitive coding tasks, strict rule execution | High-volume, low-complexity tasks. Boilerplate, repetitive patterns, tight budgets. Use when speed/cost > deliberation. |
| **Gemini** | Tool orchestration, repo navigation, large-context reasoning | Playbook — tool-aware, explore-first, task-focused | Codebase discovery, multi-file refactors, planning across a large repo | Unfamiliar codebases, cross-system tracing, tool-heavy workflows. Use when exploration > execution. |

#### Recommended Model per Agent

| Agent | Best Model | Reasoning |
|---|---|---|
| **architecture-guardian** | Claude | Doctrine-holding + judgment. Claude's core strength. |
| **backend-developer** | Claude or Qwen | Claude when the task involves cross-cutting concerns, new patterns, or complex domain logic. Qwen when it's straightforward CRUD, boilerplate, or you need speed over deliberation. |
| **business-analyst** | Claude or Gemini | Claude for structured requirements and acceptance criteria with complex business rules. Gemini for tracing requirements across a large unfamiliar codebase. |
| **data-engineer** | Gemini or Claude | Gemini when you need to trace lineage across an unfamiliar codebase. Claude when you're implementing transformations with complex business logic. Qwen works for routine SQL/dbt. |
| **frontend-developer** | Claude or Qwen | Same as backend. Claude handles state management complexity better. Qwen is fine for component boilerplate. |
| **identity-security-developer** | Claude | Non-negotiable. You want the model that won't drift from security doctrine. |
| **infrastructure-engineer** | Gemini or Claude | Gemini for exploration and blast-radius mapping. Claude for writing IaC with complex interdependencies. |
| **mobile-engineer** | Claude or Qwen | Claude when architecture patterns are complex (state machines, navigation flows). Qwen for standard screens and boilerplate. |
| **principal-engineer** | Claude | Trade-off analysis and ADRs are Claude's native mode. |
| **qe-engineer** | Claude or Qwen | Claude for test strategy, BDD, and complex automation design. Qwen for boilerplate test generation and routine coverage tasks. |
| **secops-engineer** | Claude (judge) + Gemini (scan) | Hybrid approach: Gemini scans and discovers, Claude judges against security standards. |

### Key Features

- **Multi-Model Support** - Deploy agent teams across Claude, Qwen, and Gemini
- **Extensible Integrations** - MCP (Model Context Protocol), skills, and custom plugins
- **Task Orchestration** - Integrated VibeKanban and Shortcut workflow management
- **Specialized Agents** - Pre-configured expert agents (backend, frontend, security, QA, BA, etc.)
- **Shared Skills** - Reusable slash-command skills deployed to all models
- **Idempotent Operations** - Install and uninstall agents cleanly
- **Security-First** - Safe configuration management with environment-based secrets

## Quick Start

### Prerequisites

- macOS (Darwin)
- Ansible 2.9+
- Node.js (for VibeKanban)
- Python 3.8+

<details>
<summary>Installation</summary>

1. Clone the repository:

```bash
git clone https://github.com/muhamadto/ai-agent-workforce.git
cd ai-agent-workforce
```

2. Deploy all agents locally:

```bash
ansible-playbook playbook.yml -e setup_state=present --limit local
```

3. Deploy specific agents using tags:

```bash
# Claude agents only
ansible-playbook playbook.yml -e setup_state=present --tags claude

# Qwen agents only
ansible-playbook playbook.yml -e setup_state=present --tags qwen

# Gemini agents only
ansible-playbook playbook.yml -e setup_state=present --tags gemini

# Skills only (deployed to all models)
ansible-playbook playbook.yml -e setup_state=present --tags skills

# VibeKanban only
ansible-playbook playbook.yml -e setup_state=present --tags vibe-kanban
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
    ├── qwen/                # Qwen Code agents
    ├── gemini/              # Gemini CLI agents
    ├── skills/              # Shared skills (all models)
    └── vibekanban/          # Task management tools
```

### Role-Based Design

Each AI model has a dedicated role that manages:
- Agent configurations and personas
- Model-specific settings
- Integration scripts and helpers
- Documentation and workflow guides

<details>
<summary>Agent Teams</summary>

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

### Qwen Code Agents

Located in `~/.qwen/agents/` — same specialized roles as Claude, configured for YOLO mode (auto-approve).

### Gemini CLI Agents

Located in `~/.gemini/agents/` — same specialized roles, tuned for repo-navigation-first, tool-heavy workflows.

### Shared Skills

Located in `~/.claude/skills/`, `~/.qwen/skills/`, and `~/.gemini/skills/`:

| Skill | Description |
|---|---|
| `adr` | Create Architecture Decision Records with context, options, and rationale |
| `api-review` | REST/gRPC API contract review for correctness, security, and design |
| `db-migration-review` | Review database migrations for destructive ops, locks, and missing rollbacks |
| `dependency-review` | Evaluate dependency upgrades for breaking changes, CVEs, and license compliance |
| `git-branch` | Branch lifecycle — cut from `origin/main`, sync via rebase, never merge |
| `git-commit` | Conventional Commits compliant commit messages with hook awareness |
| `github-issue-to-vibe` | Import GitHub issues into VibeKanban |
| `incident` | Incident response (detect → contain → resolve) and blameless postmortem |
| `release-notes` | Generate structured changelog from Conventional Commits between two refs |
| `run-quality-checks` | Full pre-commit quality gate — format, lint, test, SAST, SCA |
| `shortcut` | Shortcut project management via `short` CLI |
| `shortcut-to-vibe` | Import Shortcut stories into VibeKanban |
| `spike` | Time-boxed technical investigation with structured report and go/no-go outcome |
| `test-plan` | Structured test plans covering unit, integration, E2E, performance, and security |
| `threat-model` | STRIDE-based threat modelling for features and architecture changes |

</details>

<details>
<summary>Configuration</summary>

### Variables

Edit `group_vars/all.yml` to customize:

```yaml
# Control installation state
setup_state: present  # or absent

# Model configurations (future)
claude_default_model: "sonnet-4.5"
qwen_default_model: "qwen3-coder-next"
gemini_default_model: "gemini-2.0-flash"
```

</details>

## Task Management Integration

### VibeKanban

Installed globally via npm with Shortcut integration:

```bash
# Start local kanban board
vibe-kanban
```

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

<details>
<summary>Adding New Models</summary>

1. Create role directory: `roles/new-model/`
2. Add tasks in `roles/new-model/tasks/main.yml`
3. Add agent files in `roles/new-model/files/`
4. Update `playbook.yml` to include the role
5. Document in this README

</details>

<details>
<summary>Adding New Skills</summary>

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

3. Add the directory to the loop in `roles/skills/tasks/main.yml`:

```yaml
- shortcut/reference
- git-commit
- ...
- skill-name   # add here
```

4. Add a deploy task in `roles/skills/tasks/main.yml` following the existing pattern:

```yaml
- name: Deploy Skill Name SKILL.md to central skills
  copy:
    src: "skill-name/SKILL.md"
    dest: "{{ ansible_user_dir }}/.skills/skill-name/SKILL.md"
    mode: '0600'
  when: setup_state == "present"
```

5. Update the summary message in the same file.
6. Update the skills table in this README.

</details>

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting pull requests, reporting bugs, and adding new models or skills.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## Roadmap

- [x] Gemini CLI integration
- [x] Skills framework support
- [ ] MCP server configurations
- [ ] Multi-platform support (Linux, WSL)
- [ ] Agent performance metrics
- [ ] Team collaboration workflows
- [ ] Docker containerization
- [ ] CI/CD pipeline templates

## Support

- **Issues**: [GitHub Issues](https://github.com/muhamadto/ai-agent-workforce/issues)
- **Discussions**: [GitHub Discussions](https://github.com/muhamadto/ai-agent-workforce/discussions)

---

**Built with ❤️ for AI-powered development workflows**
