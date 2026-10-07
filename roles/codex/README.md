# Codex role

Deploys the same 13 specialist personas as the Claude role, adapted to native Codex TOML agents rather than Claude YAML frontmatter.
The role is opt-in: an unfiltered run of the main playbook does not install Codex configuration.

## Deployment

Use a current Codex CLI with custom-agent configuration. The role is verified with Codex CLI 0.160.1.
It registers agents explicitly through a managed config block, so it does not rely on standalone-file auto-discovery.
Python 3.11+ is required on the controller for repository agent validation and on the target for configuration validation.
Install and authenticate Codex yourself; this role does neither.

```bash
# Install Codex agents and the shared skills they reference
ansible-playbook playbook.yml -e setup_state=present --tags codex,skills --limit local

# Update only Codex agents and rules when shared skills are already installed
ansible-playbook playbook.yml -e setup_state=present --tags codex --limit local

# Preview changes
ansible-playbook playbook.yml -e setup_state=present --tags codex --limit local --check --diff

# Remove only Codex-owned configuration; keep shared skills for other clients
ansible-playbook playbook.yml -e setup_state=absent --tags codex --limit local
```

The shared skills role also manages Claude/OpenCode skill links. Installing `codex` alone creates the workforce skill link but does not download or populate shared skills.
The link may remain dangling until the shared skills role is installed. Removing Codex never removes `~/.skills` or another client's links.

## Files and preservation

| Location | Purpose |
|---|---|
| `~/.codex/ai-agent-workforce/agents/*.toml` | Role-owned native agent definitions |
| `~/.codex/ai-agent-workforce/.managed` | Ownership marker used to guard updates and removal |
| `~/.codex/agents/*.toml` | Entry-point symlinks for the native agents |
| `~/.codex/config.toml` | Managed workforce agent-registration tables; personal settings are retained |
| `~/.codex/AGENTS.md` | Symlink to the shared `~/.instructions/AGENTS.md` |
| `~/.instructions/AGENTS.md` | Canonical global rules shared by all three CLIs |
| `~/.agents/skills/ai-agent-workforce` | Namespaced symlink to the central `~/.skills` directory |

Existing `config.toml` settings are retained while a namespaced agent-registration block is added.
`auth.json`, sessions, personal agents, personal skills, model selection, reasoning effort, approvals and MCP settings are not overwritten.
Global rules use the Claude baseline in the single `instructions/AGENTS.md` source.
Shared communication, workflow, specialist-delegation and skills/safety changes belong there, not in separate client copies.
All agents inherit the parent model and reasoning settings. The architecture guardian and principal engineer additionally request a read-only sandbox and explicitly prohibit mutation in their instructions.
Parent runtime permission overrides can take precedence over an agent's sandbox setting; read-only configuration is not an independent security boundary.

Installation fails before deployment if a workforce agent entry, skills namespace or managed directory conflicts with an unmanaged personal resource.
Uninstall removes only matching symlinks, the managed config block and the marked role-owned agent directory. Replaced personal agent files are preserved.
Shared instructions and their backups survive removal. Matching existing instruction files are backed up before linking;
unfamiliar personal instructions block installation rather than being overwritten. Merge their additions into the canonical source explicitly first.
Rule/config updates retain backup copies. Empty config files can remain after uninstall.
Invalid TOML or a workforce registration outside the managed block fails before deployment. Configuration contents are excluded from Ansible output.
The complete proposed TOML is validated before any installation or removal changes. Incompatible inline `agents` tables
are rejected without rewriting personal configuration. Directory redirects, non-regular or hardlinked managed payloads,
ownership markers and configuration files are refused before mutation; marker and configuration reads do not follow symlinks.
Storage and configuration guards run on the target using its Python interpreter,
including in check mode. Trusted helper source is supplied inline, so validation
does not require uploading files or inspecting the controller's home instead.

If a non-empty `AGENTS.override.md` exists, Codex reads it instead of `AGENTS.md`; this role warns and does not modify the override.
When using a custom `CODEX_HOME`, pass its absolute path with `-e codex_home=/your/codex/home`.
The user skill location remains `~/.agents/skills` independently of `CODEX_HOME`.

## Specialist agents

Agent names match Claude Code and OpenCode exactly. Personal-file or registration collisions fail safely rather than renaming or overwriting agents:

- `architecture-guardian`
- `backend-developer`
- `business-analyst`
- `data-engineer`
- `frontend-developer`
- `identity-security-developer`
- `infrastructure-engineer`
- `mobile-engineer`
- `native-macos-engineer`
- `principal-engineer`
- `qe-engineer`
- `secops-engineer`
- `sre-engineer`

Each agent carries its own instructions and explicit skill-file references. Claude-only fields such as `tools`, `permissionMode`, `maxTurns`, `memory` and `skills` are not copied into Codex TOML.
The bodies retain specialist standards but translate skill paths and collaborator names to Codex conventions. To maintain a persona, update its Codex TOML alongside its corresponding Claude persona.

## Usage and validation

Restart Codex after installation and ask for delegation explicitly:

```text
Delegate backend implementation to backend-developer and ask
qe-engineer to verify the acceptance criteria.
```

No `codex --agent` or Claude-style `@agent` invocation is assumed. Whether a Conductor session exposes subagent tools depends on its host.
When those tools are unavailable, the global rules direct the main agent to read and apply the specialist instructions without claiming delegation occurred.

```bash
python3 scripts/validate_skill_refs.py
ansible-playbook playbook.yml --syntax-check --limit local

# Inspect loaded instructions/skills without sending a model request, on a CLI supporting this debug command
codex debug prompt-input "List loaded workforce instructions and skills"
```

The build workflow validates TOML fields, agent names, skill references and the canonical global rules in addition to Ansible lint and syntax checks.
References: [custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[skills](https://learn.chatgpt.com/docs/build-skills), and [global instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
