# Claude Code Agent Role

Deploys and manages Claude Code agent teams with specialized personas and workflow integrations.

## What This Role Does

- Creates `~/.claude` directory structure
- Deploys Claude Code settings and configuration
- Installs specialized agent personas on Anthropic Sonnet (all agents)

## Agent Personas

| Agent | Model |
|---|---|
| **architecture-guardian** | Sonnet |
| **backend-developer** | Sonnet |
| **business-analyst** | Sonnet |
| **data-engineer** | Sonnet |
| **frontend-developer** | Sonnet |
| **identity-security-developer** | Sonnet |
| **infrastructure-engineer** | Sonnet |
| **mobile-engineer** | Sonnet |
| **principal-engineer** | Sonnet |
| **qe-engineer** | Sonnet |
| **secops-engineer** | Sonnet |

## Usage

### Deploy Claude Agents

```bash
ansible-playbook playbook.yml -e setup_state=present --tags claude
```

### Remove Claude Agents

```bash
ansible-playbook playbook.yml -e setup_state=absent --tags claude
```

### Invoke Agents in Claude Code

```bash
# Automatic selection
claude "build a REST API"

# Explicit agent selection
claude "@backend-developer build a REST API"
```

## Files Deployed

### Configuration
- `~/.claude/settings.json` - Claude Code settings

### Agents
- `~/.claude/agents/*.md` - Agent persona definitions

## Requirements

- macOS
- Claude Code CLI installed
- `ANTHROPIC_API_KEY` set in the environment

## Variables

- `claude_default_model` — Default Claude model (optional override)

## Tags

- `ai` - All AI-related tasks
- `claude` - Claude-specific tasks
- `agents` - Agent deployment tasks
