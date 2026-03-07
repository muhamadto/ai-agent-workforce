# AI Agent Workforce

> Deploy AI agent teams as code. Ansible automation for multi-model AI agents with pluggable integrations, task orchestration, and workspace management.

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
| **frontend-developer** | Claude or Qwen | Same as backend. Claude handles state management complexity better. Qwen is fine for component boilerplate. |
| **data-engineer** | Gemini or Claude | Gemini when you need to trace lineage across an unfamiliar codebase. Claude when you're implementing transformations with complex business logic. Qwen works for routine SQL/dbt. |
| **identity-security-developer** | Claude | Non-negotiable. You want the model that won't drift from security doctrine. |
| **infrastructure-engineer** | Gemini or Claude | Gemini for exploration and blast-radius mapping. Claude for writing IaC with complex interdependencies. |
| **mobile-engineer** | Claude or Qwen | Claude when architecture patterns are complex (state machines, navigation flows). Qwen for standard screens and boilerplate. |
| **principal-engineer** | Claude | Trade-off analysis and ADRs are Claude's native mode. |
| **secops-engineer** | Claude (judge) + Gemini (scan) | Hybrid approach: Gemini scans and discovers, Claude judges against security standards. |

### Key Features

- 🤖 **Multi-Model Support** - Deploy agent teams across Claude, Qwen, and Gemini
- 🔧 **Extensible Integrations** - MCP (Model Context Protocol), skills, and custom plugins
- 📋 **Task Orchestration** - Integrated VibeKanban and Shortcut workflow management
- 🎯 **Specialized Agents** - Pre-configured expert agents (backend, frontend, security, etc.)
- 📦 **Idempotent Operations** - Install and uninstall agents cleanly
- 🔒 **Security-First** - Safe configuration management with environment-based secrets

## Quick Start

### Prerequisites

- macOS (Darwin)
- Ansible 2.9+
- Node.js (for VibeKanban)
- Python 3.8+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-agent-workforce.git
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

# VibeKanban only
ansible-playbook playbook.yml -e setup_state=present --tags vibe-kanban
```

### Uninstallation

Remove all agents and configurations:
```bash
ansible-playbook playbook.yml -e setup_state=absent --limit local
```

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
    ├── gemini/              # Gemini CLI agents (planned)
    └── vibe-kanban/         # Task management tools
```

### Role-Based Design

Each AI model has a dedicated role that manages:
- Agent configurations and personas
- Model-specific settings
- Integration scripts and helpers
- Documentation and workflow guides

## Agent Teams

### Claude Code Agents

Located in `~/.claude/agents/`:
- **architecture-guardian** - Clean Architecture enforcer
- **backend-developer** - Java, Spring Boot, GraalVM expert
- **data-engineer** - ETL/ELT, big data expert
- **frontend-developer** - React, Next.js, Flutter expert
- **identity-security-developer** - OAuth2, OIDC, passkeys expert
- **infrastructure-engineer** - AWS, GCP, Kubernetes expert
- **mobile-engineer** - iOS, Android, cross-platform expert
- **principal-engineer** - Strategic decision-maker
- **secops-engineer** - OWASP, security tooling expert

### Qwen Code Agents

Located in `~/.qwen/agents/` with the same specialized roles, configured for YOLO mode (auto-approve).

### Workflow Guides

- **CONVENTIONAL_COMMITS.md** - Git commit standards
- **GIT_HOOKS_GUIDE.md** - Git hook automation
- **SHORTCUT_VIBEKANBAN_WORKFLOW.md** - Task management integration

## Configuration

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

## Task Management Integration

### VibeKanban

Installed globally via npm with Shortcut integration:

```bash
# Start local kanban board
vibe-kanban

# Sync with Shortcut
shortcut-vibe-sync
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

### Adding New Models

1. Create role directory: `roles/new-model/`
2. Add tasks in `roles/new-model/tasks/main.yml`
3. Add agent files in `roles/new-model/files/`
4. Update `playbook.yml` to include the role
5. Document in this README

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## Roadmap

- [ ] Gemini CLI integration
- [ ] Skills framework support
- [ ] MCP server configurations
- [ ] Multi-platform support (Linux, WSL)
- [ ] Agent performance metrics
- [ ] Team collaboration workflows
- [ ] Docker containerization
- [ ] CI/CD pipeline templates

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-agent-workforce/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-agent-workforce/discussions)

## Acknowledgments

- Anthropic for Claude Code
- Alibaba for Qwen
- Google for Gemini
- The Ansible community

---

**Built with ❤️ for AI-powered development workflows**
