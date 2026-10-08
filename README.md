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
- Python 3.11+

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
# Claude agents only (all on Anthropic Sonnet)
ansible-playbook playbook.yml -e setup_state=present --tags claude --limit local

# opencode agents with per-agent model routing
ansible-playbook playbook.yml -e setup_state=present --tags opencode --limit local

# Skills only
ansible-playbook playbook.yml -e setup_state=present --tags skills --limit local

# Codex agents and their shared skills (opt-in)
ansible-playbook playbook.yml -e setup_state=present --tags codex,skills --limit local
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
├── .coderabbit.yaml          # Project-specific automated PR review rules
├── .gitleaksignore           # Reviewed, exact historical documentation findings
├── .github/workflows/        # Ansible, agent/rule validation, and security checks
├── playbook.yml              # Main orchestration playbook
├── inventory.ini             # Target hosts configuration
├── ansible.cfg               # Ansible settings
├── instructions/
│   └── AGENTS.md             # Single source of global rules for all three CLIs
├── group_vars/
│   └── all.yml               # Global variables and external skill selections
├── config/
│   └── agent-routing.toml    # Cross-CLI specialist routing
├── docs/
│   ├── dispatcher.md        # Coordinator usage and runtime safety boundaries
│   └── security-review.md   # Historical scan adjudication and exception rationale
├── scripts/
│   ├── dispatch_agent.py     # Standard-library native CLI dispatcher
│   └── validate_skill_refs.py # Agent, skill-reference, and global-rule validation
└── roles/
    ├── claude/              # Claude Code agents — all on Anthropic sonnet (default)
    ├── opencode/            # opencode agents with per-agent model routing (opt-in: --tags opencode)
    ├── codex/                # Native Codex agents (opt-in: --tags codex)
    │   ├── defaults/         # Codex home and managed-directory paths
    │   ├── files/            # Native agent TOML and config validation
    │   ├── templates/        # Managed agent-registration tables
    │   └── tasks/            # Safe install/remove with personal-file preservation
    ├── dispatcher/           # Private workforce command (opt-in: --tags dispatcher)
    ├── instructions/         # Shared instructions and guarded client symlinks
    │   ├── files/           # Exact historical instruction fingerprints
    │   └── tasks/           # Preflight storage guards and safe migration
    └── skills/              # Shared skills
```

The `claude` role deploys Claude Code agents to `~/.claude/` (default). The `opencode`
role deploys opencode configuration to `~/.config/opencode/` and is opt-in via `--tags opencode`.

Agents are slim personas (standards, workflow, posture); their domain knowledge lives
in lazy-loaded knowledge skills (e.g. `java-spring-engineering`, `auth-engineering`)
that agents pull in on demand via their `skills:` frontmatter.

The opt-in [Codex role](roles/codex/README.md) deploys 13 native TOML agents under
`~/.codex/agents/*.toml`, links `~/.codex/AGENTS.md` to the shared instructions,
and exposes shared skills through `~/.agents/skills/ai-agent-workforce`. It preserves
personal configuration and authentication, inherits the session's model settings,
and removes only role-owned files and links. Codex skills are loaded through explicit
instruction references rather than Claude-style frontmatter.
Agent registration is added as a managed block in `~/.codex/config.toml`; existing
personal settings are retained. All three client roles use the same specialist names.

### Cross-CLI Dispatcher

The opt-in [dispatcher role](roles/dispatcher/README.md) installs a private Python
3.11+ dispatcher and `~/.local/bin/workforce`, routing named specialists through
existing Codex, Claude Code and OpenCode CLIs. It installs no packages or CLIs and
preserves native settings, authentication and shared instruction links.

```sh
ansible-playbook playbook.yml -e setup_state=present --tags dispatcher --limit local
~/.local/bin/workforce list
~/.local/bin/workforce delegate business-analyst --task-file /absolute/path/task.txt --workspace "$PWD" --dry-run
```

`list` and `delegate --dry-run` are offline: they do not invoke native CLIs or
models. Live delegation uses existing native subscription logins, defaults to
read-only and requires explicit `--allow-write` for implementation tasks. Native
controls are not an independent operating-system sandbox. OpenCode read-only
handoffs are disabled because effective restrictions cannot be established;
write handoffs require explicit local subscription attestation and matching
cached authentication metadata. Default OpenCode routes fail closed until configured.
A successful dry run does not prove
live authentication or model access. See [dispatcher usage and safety](docs/dispatcher.md)
and the role README for routing overrides, prerequisites, collision protection
and safe removal.

### Shared Global Instructions

Edit `instructions/AGENTS.md` once. Each client role installs it as `~/.instructions/AGENTS.md`
and links its documented global instruction path to that single installed file:

- Claude Code: `~/.claude/CLAUDE.md`
- OpenCode: `~/.config/opencode/AGENTS.md`
- Codex: `~/.codex/AGENTS.md` (or the configured `codex_home`)

Exact current and recognised historical shipped files are backed up with a
`.before-ai-agent-workforce` suffix before migration. Personal additions are not
treated as shipped files. Redirected storage and multiply linked payloads are refused.
Unfamiliar files or links block installation; explicitly merge personal additions into the canonical source first.
Updates back up the installed shared file. Client removal deletes only its matching link and leaves shared instructions and backups intact.
Claude's project-level `AGENTS.md` support does not change its global `CLAUDE.md` path.
This layout targets the CLIs; Claude Cowork skips user-level instruction symlinks pointing outside its working directory.
See the [shared instructions role](roles/instructions/README.md) for instruction-only deployment.

## Agent Team

<details>
<summary>Agents</summary>

Located in `~/.claude/agents/` and `~/.config/opencode/agents/`:
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
- **sre-engineer** - SLOs, alerting, incident response, capacity, DR

</details>

## Shared Skills

### Skill Tenancy

- **Platform skills** (`sandpipers-platform`, `event-messaging`, `data-stores`,
  `observability`) describe infrastructure that outlives any project — they are wired
  permanently into agent frontmatter.
- **Domain skills** (e.g. `airline-retailing`) are added to agents per-project. When a
  second domain appears, or the project repo matures, the domain skill migrates into
  that project repo's `.claude/skills/` and is removed from the workforce frontmatter —
  per-agent skill lists must keep meaning something.
<details>
<summary>Local skills (this repo)</summary>

Deployed to `~/.skills/`, symlinked to both `~/.claude/skills/` and `~/.config/opencode/skills/`:

| Skill | What it covers |
|---|---|
| `adr` | Architecture Decision Records |
| `airline-retailing` | NDC, ONE Order, Offers & Orders, servicing flows — the order platform's ubiquitous language |
| `api-design` | OpenAPI/REST/gRPC contract design and review |
| `audit-jwt-config` | JWT algorithm confusion, claims gaps, token lifecycle |
| `auth-engineering` | OAuth 2.1, OIDC, passkeys, MFA, JWT, session management |
| `business-analysis` | Elicitation, INVEST stories, Gherkin, domain modeling |
| `clean-architecture` | Layer rules, Dependency Rule, violation catalog, ArchUnit |
| `data-engineering` | Python data tooling, orchestration, PostgreSQL+MinIO analytics |
| `data-stores` | PostgreSQL, Redis, MongoDB, MinIO, migrations, caching |
| `db-migration-review` | Destructive ops, lock analysis, missing rollbacks |
| `dependency-review` | Breaking changes, CVEs, license compliance |
| `event-messaging` | NATS JetStream, outbox pattern, CDC, streaming |
| `frontend-engineering` | React 18+, Next.js 14+, Flutter 3.x, testing stack |
| `git-branch` | Branch lifecycle — cut from `origin/main`, sync via rebase |
| `git-commit` | Conventional Commits with hook awareness |
| `incident` | Detect → contain → resolve, blameless postmortem |
| `infrastructure-engineering` | AWS/GCP, Kubernetes, Pulumi Java, private-cloud stack |
| `java-spring-engineering` | Java 24+, Spring Boot 4.x, GraalVM Native, Maven toolchain |
| `junit5` | JUnit 5 patterns, parameterized tests, Testcontainers |
| `microservice-template` | Maven multi-module layout: client / service / infra (Pulumi Java) |
| `mobile-engineering` | Swift/SwiftUI, Kotlin/Compose, Flutter, store distribution |
| `modulith-template` | Maven Spring Modulith layout: contracts / app / infra (Pulumi Java) |
| `oauth-threat-model` | OAuth2/OIDC flows: PKCE, redirect URIs, token theft |
| `observability` | Micrometer/Prometheus, Loki, OpenTelemetry/Tempo, SLO alerting |
| `openapi` | OpenAPI 3.1 spec authoring rules and HTTP status codes |
| `quality-engineering` | Test strategy, BDD, performance, CI/CD quality gates |
| `release-notes` | Structured changelog from Conventional Commits |
| `run-quality-checks` | Full pre-commit gate: format, lint, test, SAST, SCA |
| `sandpipers-platform` | Private-cloud service map (NATS not SQS, Keycloak not Cognito, MinIO not S3) |
| `secops-engineering` | OWASP Top 10, SAST/DAST/SCA tooling, supply chain |
| `shortcut` | Shortcut project management via `short` CLI |
| `spike` | Time-boxed investigation with go/no-go outcome |
| `test-plan` | Unit, integration, E2E, performance, and security coverage |
| `threat-model` | STRIDE threat modelling for features and architecture |
| `validation` | Input validation patterns at system boundaries |

</details>

<details>
<summary>GitHub-sourced skills (<code>group_vars/all.yml</code>)</summary>

Cloned to `~/.skills/.cache/repos/` and synced to `~/.skills/` on every playbook run:

| Skill | Source repo |
|---|---|
| `test-driven-development` | `obra/superpowers` |
| `systematic-debugging` | `obra/superpowers` |
| `context7-cli` | `upstash/context7` |
| `find-docs` | `upstash/context7` |
| `mcp-builder` | `anthropics/skills` |
| `skill-creator` | `anthropics/skills` |
| `caveman` | `juliusbrussee/caveman` |
| `playwright-cli` | `microsoft/playwright-cli` |
| `sonarcloud-analysis` | `harshanandak/forge` |
| `grill-me` | `mattpocock/skills` |

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

# Validate Claude skill references and native Codex agent definitions
python3 scripts/validate_skill_refs.py

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

SSH host verification is enforced. Any separately approved remote use requires host keys verified through a trusted channel and pre-provisioned in known_hosts; unknown or changed keys must fail. Never use automatic acceptance, disabled verification or an empty trust store as a workaround. The supported setup launcher remains local-only.
