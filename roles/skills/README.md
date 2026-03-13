# Skills Role

Shared AI agent skills deployed to all models (Claude, Qwen, Gemini).

## Structure

```
roles/skills/
├── files/
│   └── <skill-name>/
│       ├── SKILL.md              # Instructions the AI reads
│       └── reference/            # Supporting reference docs
│           └── *.json            # API specs, schemas, etc.
└── tasks/
    └── main.yml
```

Each skill is deployed to:
```
~/.claude/skills/<skill-name>/
~/.qwen/skills/<skill-name>/
~/.gemini/skills/<skill-name>/
```

## Skills

| Skill | Description | Requires |
|---|---|---|
| `shortcut` | Shortcut project management via `short` CLI | `short` CLI installed and authenticated |
| `shortcut-to-vibe` | Import Shortcut stories into VibeKanban | `short` CLI + VibeKanban MCP server running |

## Usage

```bash
# Deploy all skills
ansible-playbook playbook.yml -e setup_state=present --tags skills

# Remove all skills
ansible-playbook playbook.yml -e setup_state=absent --tags skills
```

## Adding a New Skill

1. Create `roles/skills/files/<skill-name>/SKILL.md`
2. Add any reference files to `roles/skills/files/<skill-name>/reference/`
3. Add directory creation, deployment, and removal tasks to `tasks/main.yml`
4. Update this README

## Model Support

Skills work differently across models. The table below summarises how each model discovers and invokes skills.

| Model | Skill discovery | `skills:` frontmatter | How to wire a skill |
|---|---|---|---|
| Claude Code | Native — reads `skills:` frontmatter and exposes skills as `/skill-name` slash commands | **Processed** — list skills here and Claude will use them | Add `- skill-name` under `skills:` in the agent frontmatter |
| Gemini CLI | Autonomous — scans `~/.gemini/skills/` and matches skills by description at runtime | **Ignored** — parsed as unknown YAML, has no effect | Reference the skill explicitly in the agent body (e.g. `## Workflow` step or `## Documenting Decisions`) |
| Qwen Code | Autonomous — scans `~/.qwen/skills/` and matches skills by description at runtime | **Ignored** — parsed as unknown YAML, has no effect | Reference the skill explicitly in the agent body |

### Convention for agent frontmatter

All agent files include a `skills:` block regardless of model. For Claude it drives behaviour; for Gemini and Qwen it is documentation only — a comment in the file makes this explicit:

Claude agent — `skills:` is processed:

```yaml
skills:
  - git-commit
  - api-design
```

Gemini / Qwen agent — `skills:` is for readability only, with an explanatory comment:

```yaml
# Skills listed for readability only — not processed by Gemini CLI
skills:
  - git-commit
  - api-design
```

For Gemini and Qwen agents, always pair the `skills:` block with an explicit body reference so the model actually invokes the skill:

```markdown
## Workflow
- Use the [/api-design](../skills/api-design/SKILL.md) skill to review the contract before merging
- Commit using the [/git-commit](../skills/git-commit/SKILL.md) skill
```

## Notes

- The Shortcut OpenAPI spec is downloaded from `https://developer.shortcut.com/api/rest/v3/shortcut.openapi.json` at deploy time — always current, no auth required
