# Qwen Code Agent Role

Deploys and manages Qwen Code agent teams with YOLO-mode configuration (auto-approve all tools).

## What This Role Does

- Creates `~/.qwen` directory structure
- Deploys Qwen Code settings with YOLO mode enabled
- Installs specialized agent personas (mirroring Claude agents)
- Configures automatic tool approval for faster development

## Agent Personas

All agents use Qwen3-Coder-Next model:

- **architecture-guardian.md** - Clean Architecture enforcer
- **backend-developer.md** - Java 24+, Spring Boot 4.x, Spring Native expert
- **data-engineer.md** - ETL/ELT, big data specialist
- **frontend-developer.md** - React, Next.js, Flutter expert
- **identity-security-developer.md** - OAuth2, OIDC security expert
- **infrastructure-engineer.md** - AWS, GCP, K3S specialist
- **mobile-engineer.md** - iOS, Android, Flutter expert
- **principal-engineer.md** - Strategic decision-maker
- **secops-engineer.md** - OWASP, security tooling expert

## YOLO Mode

Qwen agents are configured with auto-approve for all tools, enabling:
- Faster development cycles
- Reduced interruptions for confirmations
- Autonomous agent operation

**⚠️ Use with caution in production environments**

## Usage

### Deploy Qwen Agents

```bash
ansible-playbook playbook.yml -e setup_state=present --tags qwen
```

### Remove Qwen Agents

```bash
ansible-playbook playbook.yml -e setup_state=absent --tags qwen
```

### Invoke Agents in Qwen Code

Qwen automatically delegates to appropriate subagents based on task context.

## Files Deployed

### Configuration
- `~/.qwen/settings.json` - Qwen Code settings with YOLO mode

### Agents
- `~/.qwen/agents/*.md` - Agent persona definitions

## Requirements

- macOS
- Qwen Code CLI installed
- Qwen API access configured

## Variables

None currently. Future:
- `qwen_default_model` - Default Qwen model to use
- `qwen_yolo_mode` - Toggle YOLO mode (default: true)

## Tags

- `ai` - All AI-related tasks
- `qwen` - Qwen-specific tasks
- `agents` - Agent deployment tasks
