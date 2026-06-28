# opencode role

Deploys and manages opencode agent configurations with per-agent model routing. Deploys to `~/.config/opencode/`:

- **`opencode.jsonc`** — global defaults (model, permissions); agents are NOT listed here
- **`AGENTS.md`** — global operating rules (workflow, story lifecycle, hard stops); auto-loaded by opencode without any config
- **`agents/*.md`** — 12 specialist agents, one markdown file each with YAML frontmatter

Each agent file follows the opencode markdown format: YAML frontmatter (`model`, `description`, `mode`, `steps`, `permission`) and a markdown body that becomes the system prompt.

## Model routing

| Agent | Model | Permissions |
|---|---|---|
| `architecture-guardian` | `glm-5.2:cloud` | read-only — no edit/bash |
| `principal-engineer` | `glm-5.2:cloud` | read-only — no edit/bash |
| `business-analyst` | `glm-5.2:cloud` | full |
| `qe-engineer` | `glm-5.2:cloud` | full |
| `secops-engineer` | `glm-5.2:cloud` | full |
| `sre-engineer` | `glm-5.2:cloud` | full |
| `backend-developer` | `glm-5.2:cloud` | full |
| `data-engineer` | `glm-5.2:cloud` | full |
| `identity-security-developer` | `glm-5.2:cloud` | full |
| `infrastructure-engineer` | `glm-5.2:cloud` | full |
| `frontend-developer` | `kimi-k2.7-code` | full |
| `mobile-engineer` | `kimi-k2.7-code` | full |

Interactive sessions (no agent selected) use the global default: `glm-5.2:cloud`. To change it, edit the `model` field in `opencode.jsonc`.

## Requirements

- macOS
- opencode installed (`brew install opencode`)
- `ANTHROPIC_API_KEY` set in the environment (for advisory agents)
- Authenticated with `ollama-cloud` provider (`opencode providers` → follow auth flow)

## Deployment

```bash
# Deploy
ansible-playbook playbook.yml -e setup_state=present --tags opencode --limit local

# Remove
ansible-playbook playbook.yml -e setup_state=absent --tags opencode --limit local
```

## Usage

```bash
# Interactive TUI — select agent from the agent picker
opencode

# Run a specific agent non-interactively
opencode run --agent backend-developer "implement the feature"
opencode run --agent architecture-guardian "review this PR"
opencode run --agent qe-engineer "write tests for the service"
```

## Mutual exclusivity

The `claude` and `opencode` roles configure different tools (`~/.claude/` vs `~/.config/opencode/`) so they are **not** mutually exclusive at the file level — but they represent different AI coding workflows and should not be used simultaneously for the same task.
