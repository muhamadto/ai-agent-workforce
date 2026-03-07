# CLAUDE.md

This file provides guidance to Claude Code when working with the AI Agent Workforce project.

## Project Overview

AI Agent Workforce is an Ansible automation tool for deploying and managing AI agent teams across multiple models (Claude, Qwen, Gemini) with task orchestration integration.

## Common Commands

### Running the Playbook

**Local deployment:**
```bash
ansible-playbook playbook.yml -e setup_state=present --limit local
```

**Remote deployment:**
```bash
ansible-playbook playbook.yml -e setup_state=present --limit remote --ask-become-pass
```

**Deploy specific agents:**
```bash
# Claude only
ansible-playbook playbook.yml -e setup_state=present --tags claude

# Qwen only
ansible-playbook playbook.yml -e setup_state=present --tags qwen

# VibeKanban only
ansible-playbook playbook.yml -e setup_state=present --tags vibe-kanban
```

**Uninstall:**
```bash
ansible-playbook playbook.yml -e setup_state=absent --limit local
```

### Testing & Validation

```bash
# Syntax check
ansible-playbook playbook.yml --syntax-check

# Dry run
ansible-playbook playbook.yml --check

# Debug mode
ansible-playbook playbook.yml -vvvv
```

## Architecture

### Project Structure

```
ai-agent-workforce/
├── playbook.yml              # Main orchestration
├── inventory.ini             # Target hosts
├── ansible.cfg               # Ansible configuration
├── group_vars/all.yml        # Global variables
└── roles/
    ├── claude/              # Claude Code agents
    │   ├── tasks/main.yml
    │   ├── files/
    │   │   ├── settings.json
    │   │   ├── agents/*.md
    │   │   └── *.md (guides)
    │   └── README.md
    ├── qwen/                # Qwen Code agents
    │   ├── tasks/main.yml
    │   ├── files/
    │   │   ├── settings.json
    │   │   └── agents/*.md
    │   └── README.md
    ├── gemini/              # Gemini CLI (placeholder)
    │   ├── tasks/main.yml
    │   └── README.md
    └── vibe-kanban/         # Task management
        ├── tasks/main.yml
        ├── files/shortcut-vibe-sync.sh
        └── README.md
```

### Role Design Patterns

Each AI model role follows this structure:
1. Create config directory (`~/.model-name/`)
2. Deploy settings.json
3. Create agents directory
4. Deploy agent personas
5. Deploy helper scripts and guides
6. Cleanup tasks for removal (`setup_state=absent`)

### Key Variables

- `setup_state`: Controls install (present) or uninstall (absent)
- Future: model-specific configurations in `group_vars/all.yml`

## Coding Standards

### Ansible Best Practices

1. **License headers**: All task files must include Apache 2.0 header
2. **Idempotent operations**: Use `setup_state` variable
3. **Descriptive names**: Clear task names with `name:` field
4. **Tags**: Add relevant tags to all roles and task groups
5. **Debug messages**: Provide user feedback on success/failure
6. **Conditional execution**: Use `when: setup_state == "present"` or `"absent"`

### File Organization

- Tasks: `roles/*/tasks/main.yml`
- Static files: `roles/*/files/`
- Variables: `roles/*/defaults/main.yml` (future)
- Documentation: `roles/*/README.md`

### Commit Messages

Follow Conventional Commits:
- `feat(scope): description` - New features
- `fix(scope): description` - Bug fixes
- `docs(scope): description` - Documentation
- `chore(scope): description` - Maintenance

## Adding New AI Models

When adding a new model (e.g., Gemini, Mistral):

1. **Create role directory**: `roles/model-name/`
2. **Implement tasks**: Based on claude/qwen patterns
3. **Add agent files**: Settings and persona definitions
4. **Update playbook.yml**: Include the new role
5. **Write README**: Document usage and requirements
6. **Test thoroughly**: Install, verify, uninstall

## Testing Workflow

```bash
# 1. Syntax validation
ansible-playbook playbook.yml --syntax-check

# 2. Dry run
ansible-playbook playbook.yml --check

# 3. Install locally
ansible-playbook playbook.yml -e setup_state=present --limit local

# 4. Verify installation
ls -la ~/.claude/ ~/.qwen/

# 5. Test removal
ansible-playbook playbook.yml -e setup_state=absent --limit local

# 6. Verify cleanup
# Directories should be removed
```

## Common Tasks for Claude

### Adding a New Agent Persona

1. Create agent file in `roles/claude/files/agents/new-agent.md`
2. Update `roles/claude/tasks/main.yml` loop to include new agent
3. Document in role README
4. Test deployment

### Updating Workflow Guides

Shared guides are in:
- `roles/claude/files/CONVENTIONAL_COMMITS.md`
- `roles/claude/files/GIT_HOOKS_GUIDE.md`
- `roles/claude/files/SHORTCUT_VIBEKANBAN_WORKFLOW.md`

Copy to both Claude and Qwen if changes affect both.

### Adding New Model Support

See "Adding New AI Models" section above.

## Important Notes

- **macOS only**: Playbook includes Darwin platform check
- **Idempotent**: All operations should be safely re-runnable
- **No secrets in repo**: Use environment variables for API keys
- **License compliance**: Apache 2.0 headers required
- **Documentation**: Keep READMEs in sync with changes

## Dependencies

- Ansible 2.9+
- macOS (Darwin)
- Node.js (for VibeKanban)
- Python 3.8+

## Future Enhancements

- Multi-platform support (Linux, WSL)
- Skills framework integration
- MCP server configurations
- Agent performance metrics
- Docker containerization
- CI/CD pipeline templates
