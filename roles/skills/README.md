# Skills Role

Shared AI agent skills deployed to `~/.skills/` with a symlink from `~/.claude/skills/`.

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

Skills are deployed to `~/.skills/` and symlinked into `~/.claude/skills/` so Claude Code exposes them as `/skill-name` slash commands.

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
3. Update this README

The copy task in `tasks/main.yml` auto-discovers all directories under `roles/skills/files/` — no task changes needed.

## How Claude Code Uses Skills

Claude Code reads the `skills:` frontmatter in agent files and exposes each listed skill as a `/skill-name` slash command:

```yaml
skills:
  - git-commit
  - api-design
```

## Notes

- The Shortcut OpenAPI spec is downloaded from `https://developer.shortcut.com/api/rest/v3/shortcut.openapi.json` at deploy time — always current, no auth required
