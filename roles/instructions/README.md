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

Recognised existing files are copied to `<entry-point>.before-ai-agent-workforce` before becoming links.
An existing backup is never overwritten. If it preserves another revision, the outgoing file is
saved to `<entry-point>.before-ai-agent-workforce.<sha256>` instead; an existing selected backup
must contain exactly that outgoing revision. All backup guards run before mutation.
Recognition uses whole-payload SHA256: the exact current
repository source or a shipped historical payload in `files/legacy-fingerprints.json`. Each historical
digest records its source path and full Git commit, researched across this branch and `origin/main`.
Digests cover the complete original bytes, including the final newline and maintenance note. To verify provenance,
hash `git show <commit>:<path>` with SHA256. Only a single complete pair of exact outer
`<!-- BEGIN AI AGENT WORKFORCE -->` / `<!-- END AI AGENT WORKFORCE -->` lines may be removed;
both markers require their final newline. No whitespace trimming, maintenance-note removal, internal
marker removal, partial matching or similarity checks are permitted. Empty files, different personal
rules, directories and unfamiliar symlinks block installation without replacing them. Explicitly merge
desired personal additions into the canonical repository source, then rerun. Backups do not automatically
restore on uninstall; remove the managed link first and restore a backup explicitly if desired.

Before reading payloads or changing anything, all shared-storage and destination directory ancestors
must be absent or real directories, never symlinks. Existing ownership markers, canonical payloads,
migration backups and regular entry points must be single-link regular files; dangling symlinks,
hardlinks and special files are refused. Only the exact managed client link is permitted.
The shared directory must be absent or have this role's `.managed` ownership marker.
Its value is `ai-agent-workforce:instructions`, with an optional final newline.
Legacy `ai-agent-workforce` markers migrate only at the original `~/.instructions`
path after the existing canonical-payload checks pass. For legacy custom paths,
verify ownership explicitly before replacing the marker; never relabel another
role's directory. Managed role roots, shared skills and configured canonical
instructions must not overlap, including through resolved aliases.
Canonical updates
retain Ansible's timestamped backups; existing backups are inspected without following links and
must be single-link regular files. Ansible names backups using the module PID and timestamp, then
copies with `shutil.copy2`, not an exclusive-create primitive: validating existing backup paths and
the private storage directory is required, rather than assuming the helper refuses redirects.
Unrecognised shared payloads (including personal additions) block installation. Recognised successive
updates do not require manually archiving earlier backups. Edit the repository source rather than
the installed file. These are preflight checks, not an atomic defence against a concurrent filesystem
attacker swapping paths after validation.
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
