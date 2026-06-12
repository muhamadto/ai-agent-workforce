# Claude Code Agent Role

Deploys and manages Claude Code agent teams with specialized personas and workflow integrations.

## What This Role Does

- Creates `~/.claude` directory structure
- Deploys Claude Code settings and configuration
- Installs specialized agent personas with per-agent model routing via LiteLLM

## Agent Personas

| Agent | Model |
|---|---|
| **architecture-guardian** | Sonnet |
| **backend-developer** | glm-5.1:cloud |
| **business-analyst** | Sonnet |
| **data-engineer** | glm-5.1:cloud |
| **frontend-developer** | kimi-k2.6:cloud |
| **identity-security-developer** | glm-5.1:cloud |
| **infrastructure-engineer** | glm-5.1:cloud |
| **mobile-engineer** | glm-5.1:cloud |
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
- LiteLLM configured and running (for model routing)

## Variables

- `claude_default_model` — Default Claude model (optional override)

## Tags

- `ai` - All AI-related tasks
- `claude` - Claude-specific tasks
- `agents` - Agent deployment tasks
