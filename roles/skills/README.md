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

All three models support native skill discovery — no flags or extra configuration required.

| Model | Skills stable since |
| --- | --- |
| Claude Code | Native |
| Gemini CLI | Native |
| Qwen Code | v0.9.0 |

## Notes

- The Shortcut OpenAPI spec is downloaded from `https://developer.shortcut.com/api/rest/v3/shortcut.openapi.json` at deploy time — always current, no auth required
