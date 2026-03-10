# Contributing to AI Agent Workforce

Thank you for your interest in contributing! This document covers how to report bugs, suggest features, submit pull requests, and extend the project with new models or skills.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Assume good intentions

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/muhamadto/ai-agent-workforce/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Ansible version, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. Check [existing feature requests](https://github.com/muhamadto/ai-agent-workforce/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
2. Open a new issue with:
   - Clear use case and motivation
   - Proposed solution or API
   - Alternative approaches considered
   - Willingness to implement it yourself

### Pull Requests

1. Fork the repository and create a feature branch from `main`:

   ```bash
   git fetch origin
   git checkout -b feat/your-feature-name origin/main
   ```

2. Make your changes following the coding standards below.

3. Test your changes:

   ```bash
   # Syntax check
   ansible-playbook playbook.yml --syntax-check

   # Dry run
   ansible-playbook playbook.yml --check

   # Test installation
   ansible-playbook playbook.yml -e setup_state=present --limit local

   # Test removal
   ansible-playbook playbook.yml -e setup_state=absent --limit local
   ```

4. Commit using [Conventional Commits](https://www.conventionalcommits.org/) with a `Signed-off-by` footer:

   ```
   feat(skills): add spike skill for technical investigations

   Signed-off-by: Your Name <your@email.com>
   ```

   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `build`, `perf`

5. Push and open a pull request against `main`:

   ```bash
   git push -u origin feat/your-feature-name
   ```

## Coding Standards

### Ansible Style

- Use 2-space indentation (YAML standard)
- Include license header in all task files
- Use descriptive task names with `name:` field
- Add tags for all roles and major task groups
- Use `setup_state` variable for idempotent operations
- Add debug messages for user feedback

### File Organization

```
roles/model-name/
├── defaults/
│   └── main.yml        # Default variables
├── files/              # Static files to deploy
│   ├── settings.json
│   └── agents/
└── tasks/
    └── main.yml        # Task definitions
```

### Documentation

- Update `README.md` for new features
- Add role-specific `README.md` in each role directory
- Include usage examples
- Document all variables

## Adding New AI Models

1. Create role structure:

   ```bash
   mkdir -p roles/model-name/{tasks,files,defaults}
   ```

2. Implement tasks in `roles/model-name/tasks/main.yml`:
   - Directory creation
   - File deployment
   - Configuration management
   - Cleanup tasks (when `setup_state == "absent"`)

3. Add agent files to `roles/model-name/files/`:
   - `settings.json`
   - Agent definitions under `agents/`

4. Update `playbook.yml`:

   ```yaml
   - role: model-name
     tags:
       - ai
       - model-name
       - agents
   ```

5. Update `README.md`:
   - Add to supported models list
   - Add to the recommended-model-per-agent table
   - Update usage examples

## Adding New Skills

1. Create the skill directory:

   ```bash
   mkdir roles/skills/files/<skill-name>
   ```

2. Write `roles/skills/files/<skill-name>/SKILL.md` with a frontmatter header:

   ```markdown
   ---
   name: skill-name
   description: One-sentence description shown in the skills list.
   ---

   # Skill Name

   ...
   ```

3. Add the directory name to the loop in `roles/skills/tasks/main.yml`:

   ```yaml
   loop:
     - shortcut/reference
     - git-commit
     - ...
     - skill-name   # add here
   ```

4. Add a deploy task in the same file, following the existing pattern:

   ```yaml
   - name: Deploy Skill Name SKILL.md to central skills
     copy:
       src: "skill-name/SKILL.md"
       dest: "{{ ansible_user_dir }}/.skills/skill-name/SKILL.md"
       mode: '0600'
     when: setup_state == "present"
   ```

5. Update the summary message in the same file.
6. Update the skills table in `README.md`.

## Testing Guidelines

Always test both installation and removal:

```bash
# Install
ansible-playbook playbook.yml -e setup_state=present --limit local --tags your-role

# Verify installation
ls -la ~/.model-name/

# Remove
ansible-playbook playbook.yml -e setup_state=absent --limit local --tags your-role

# Verify removal
ls -la ~/.model-name/  # Should not exist
```

### Edge Cases to Test

- First-time installation (directories don't exist)
- Re-running installation (idempotency)
- Partial removal (some files missing)
- Permission issues
- Missing dependencies

## Questions?

- Open a [Discussion](https://github.com/muhamadto/ai-agent-workforce/discussions)
- Or file an [Issue](https://github.com/muhamadto/ai-agent-workforce/issues)

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
