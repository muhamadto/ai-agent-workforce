# Claude Code Agent Role

Deploys and manages Claude Code agent teams with specialized personas and workflow integrations.

## What This Role Does

- Creates `~/.claude` directory structure
- Deploys Claude Code settings and configuration
- Installs specialized agent personas
- Sets up workflow guides (Git, Conventional Commits, Shortcut/VibeKanban)
- Configures Shortcut-Vibe sync helper script

## Agent Personas

All agents use Claude Sonnet 4.5:

- **architecture-guardian.md** - Ruthless Clean Architecture enforcer
- **backend-developer.md** - Java 24+, Spring Boot 4.x, Spring Native expert
- **data-engineer.md** - ETL/ELT, big data, data warehousing specialist
- **frontend-developer.md** - React 18+, Next.js 14+, Flutter 3.x expert
- **identity-security-developer.md** - OAuth2, OIDC, passkeys security expert
- **infrastructure-engineer.md** - AWS, GCP, Kubernetes, private cloud specialist
- **mobile-engineer.md** - iOS, Android, Flutter, React Native expert
- **principal-engineer.md** - Strategic arbiter and decision-maker
- **secops-engineer.md** - OWASP, security tooling paranoid expert

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

### Workflow Guides
- `~/.claude/CONVENTIONAL_COMMITS.md`
- `~/.claude/GIT_HOOKS_GUIDE.md`
- `~/.claude/SHORTCUT_VIBEKANBAN_WORKFLOW.md`

### Helper Scripts
- `~/.local/bin/shortcut-vibe-sync` - Shortcut ↔ VibeKanban sync

## Requirements

- macOS
- Claude Code CLI installed
- Anthropic API key configured

## Variables

None currently. Future:
- `claude_default_model` - Default Claude model to use
- `claude_api_key` - API key (prefer environment variables)

## Tags

- `ai` - All AI-related tasks
- `claude` - Claude-specific tasks
- `agents` - Agent deployment tasks
