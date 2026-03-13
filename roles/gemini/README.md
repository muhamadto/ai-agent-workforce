# Gemini CLI Agent Role

Deploys and manages Gemini CLI agent teams with auto-edit configuration.

## What This Role Does

- Creates `~/.gemini` directory structure
- Deploys Gemini CLI settings with auto-edit mode enabled
- Installs specialized agent personas
- Skills are provided via symlink to the shared `~/.skills/` directory

## Agent Personas

All agents use gemini-2.5-pro model:

- **architecture-guardian.md** - Clean Architecture enforcer
- **backend-developer.md** - Java 24+, Spring Boot 4.x expert
- **business-analyst.md** - Requirements, user stories, domain modeling
- **data-engineer.md** - ETL/ELT, dbt, Spark, data quality
- **frontend-developer.md** - React, Next.js, Flutter expert
- **identity-security-developer.md** - OAuth2, OIDC, zero-trust specialist
- **infrastructure-engineer.md** - AWS, GCP, Kubernetes, Terraform
- **mobile-engineer.md** - iOS, Android, Flutter, React Native
- **principal-engineer.md** - Strategic arbiter, cross-system view
- **qe-engineer.md** - Test strategy, automation, BDD, performance
- **secops-engineer.md** - OWASP, security tooling, paranoid by design

## Structure

```
~/.gemini/
├── settings.json          # Gemini CLI configuration
├── agents/                # Agent definitions
│   ├── architecture-guardian.md
│   ├── backend-developer.md
│   └── ...
└── skills -> ~/.skills/   # Symlink to shared skills
```

## Usage

### Deploy Gemini Agents

```bash
ansible-playbook playbook.yml -e setup_state=present --tags gemini
```

### Remove Gemini Agents

```bash
ansible-playbook playbook.yml -e setup_state=absent --tags gemini
```

### Invoke Agents in Gemini CLI

Use `@agent-name` in Gemini CLI or configure as the default agent.

## Requirements

- macOS
- Gemini CLI installed
- Google AI Studio API key or OAuth configured

## Variables

None currently.
