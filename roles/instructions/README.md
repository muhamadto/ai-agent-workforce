# Shared instructions

The single repository source is `instructions/AGENTS.md`. This role installs it with mode `0600`
in the role-owned `~/.instructions` directory (mode `0700`) and creates one client link per invocation.
Claude, OpenCode and Codex call it automatically during installation. Their removal tasks delete only
their exact link; the shared file remains available to the other clients.

| Client | Global entry point |
|---|---|
| Claude Code | `~/.claude/CLAUDE.md` |
| OpenCode | `~/.config/opencode/AGENTS.md` |
| Codex | `~/.codex/AGENTS.md` or the configured Codex home |

Do not rename Claude's global file to `~/.claude/AGENTS.md`: current project-level `AGENTS.md`
support does not document that path for global instructions. This layout is intended for the CLIs;
Claude Cowork skips user-scope instruction symlinks pointing outside its working directory.

## Migration and safety

Matching existing files are copied to `<entry-point>.before-ai-agent-workforce` before becoming links.
An existing backup is never overwritten. Matching ignores only the old maintenance note and this
repository's former managed-block markers; all other text must match. Empty files, different personal
rules, directories and unfamiliar symlinks block installation without replacing them. Explicitly merge
desired personal additions into the canonical repository source, then rerun. Backups do not automatically
restore on uninstall; remove the managed link first and restore a backup explicitly if desired.

The shared directory must be absent or have this role's `.managed` ownership marker. Updates back up
the shared file before replacing it, so edit the repository source rather than the installed file.
Client removal preserves regular files and replacement links, the shared directory and all backups.
No instruction text is logged during migration. A non-empty Codex `AGENTS.override.md` still takes precedence.

## Instruction-only deployment

Use a small playbook without the client roles to avoid changing models, settings, agents or skills:

```yaml
- name: Install shared CLI instructions
  hosts: all
  gather_facts: true
  tasks:
    - name: Link each CLI's global instructions
      ansible.builtin.include_role:
        name: instructions
      vars:
        instructions_destination: "{{ item }}"
      loop:
        - "{{ ansible_facts['user_dir'] }}/.claude/CLAUDE.md"
        - "{{ ansible_facts['user_dir'] }}/.config/opencode/AGENTS.md"
        - "{{ ansible_facts['user_dir'] }}/.codex/AGENTS.md"
```

Run it with this repository's roles on `ANSIBLE_ROLES_PATH`. Use `--check` first and restart the CLIs
after deployment. Custom `CODEX_HOME` requires changing the Codex entry point accordingly.

References: [Claude instructions](https://code.claude.com/docs/en/memory),
[OpenCode rules](https://opencode.ai/docs/rules/),
and [Codex global guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
