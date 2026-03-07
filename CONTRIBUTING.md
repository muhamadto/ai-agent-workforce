# Contributing to AI Agent Workforce

Thank you for your interest in contributing to AI Agent Workforce! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Assume good intentions

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/ai-agent-workforce/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Ansible version, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. Check [existing feature requests](https://github.com/yourusername/ai-agent-workforce/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
2. Open a new issue with:
   - Clear use case and motivation
   - Proposed solution or API
   - Alternative approaches considered
   - Willingness to implement it yourself

### Pull Requests

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**
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

4. **Commit with conventional commits**
   ```bash
   git commit -m "feat: add gemini role implementation"
   git commit -m "fix: correct claude agent deployment path"
   git commit -m "docs: update README with new examples"
   ```

   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
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
├── README.md           # Role documentation
├── defaults/
│   └── main.yml       # Default variables
├── files/             # Static files to deploy
│   ├── settings.json
│   └── agents/
├── tasks/
│   └── main.yml       # Task definitions
└── meta/
    └── main.yml       # Role metadata (optional)
```

### Documentation

- Update README.md for new features
- Add role-specific README in each role directory
- Include usage examples
- Document all variables
- Keep CHANGELOG.md updated

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Examples:
```
feat(gemini): add gemini CLI role implementation
fix(claude): correct agent deployment permissions
docs(readme): add troubleshooting section
chore(deps): update ansible to 2.15
```

## Adding New AI Models

To add support for a new AI model:

1. **Create role structure**
   ```bash
   mkdir -p roles/model-name/{tasks,files,defaults}
   ```

2. **Implement tasks** in `roles/model-name/tasks/main.yml`
   - Directory creation
   - File deployment
   - Configuration management
   - Cleanup tasks (when `setup_state == "absent"`)

3. **Add agent files** to `roles/model-name/files/`
   - settings.json
   - agent definitions
   - helper scripts

4. **Update playbook.yml**
   ```yaml
   - role: model-name
     tags:
       - ai
       - model-name
       - agents
   ```

5. **Document in README.md**
   - Add to supported models list
   - Update usage examples
   - Document any special requirements

6. **Create role README** at `roles/model-name/README.md`

## Testing Guidelines

### Local Testing

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

- Open a [Discussion](https://github.com/yourusername/ai-agent-workforce/discussions)
- Join our community chat (if available)
- Tag maintainers in issues

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
