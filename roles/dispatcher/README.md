# Dispatcher role

Opt-in installation of the cross-CLI workforce dispatcher. Requires an existing
Python 3.11+ interpreter and the repository's dispatcher script, routing TOML and
Codex persona files. This role never installs packages or native CLIs, calls a
model, changes native models/settings/authentication, or manages shared
instruction links. Deploy named Claude/OpenCode agents separately if routing to
those clients.

## Deployment

From the repository root, with the role registered using `never`/`dispatcher` tags:

```sh
ansible-playbook playbook.yml -e setup_state=present --tags dispatcher --check
ansible-playbook playbook.yml -e setup_state=present --tags dispatcher
ansible-playbook playbook.yml -e setup_state=absent --tags dispatcher
```

Defaults:

| Variable | Default |
| --- | --- |
| `dispatcher_home` | `~/.local/share/ai-agent-workforce/dispatcher` |
| `dispatcher_command` | `~/.local/bin/workforce` |
| `dispatcher_python` | `python3` |

Override home/command with absolute paths and Python with an executable name or
absolute path. A read-only version check runs even in check mode, before any
mutation. The wrapper records the resolved interpreter and forwards every
argument unchanged. Add `~/.local/bin` to your shell's `PATH` separately.
Choose a stable interpreter outside a disposable workspace or virtual
environment when overriding `dispatcher_python`; archiving that workspace must
not remove the installed command's interpreter.

The private installation contains `scripts/dispatch_agent.py`,
`config/agent-routing.toml`, `roles/codex/files/agents/*.toml`, `bin/workforce`
and the `.managed` ownership marker. Directories and the wrapper use `0700`;
sources, routing, personas and marker use `0600`. The public command is an exact
symlink to `dispatcher_home/bin/workforce`.

## Use

```sh
workforce list
workforce doctor
workforce --config /absolute/path/agent-routing.toml list
workforce delegate backend-developer --task-file /absolute/path/task.txt --workspace /absolute/git/workspace --dry-run
workforce delegate backend-developer --task-file /absolute/path/task.txt --workspace /absolute/git/workspace --allow-write --timeout 120
```

The default routing file is the installed `config/agent-routing.toml`, not a
client settings file. Use existing native CLI logins; this role does not create
an authentication cache. Read-only delegation is the default; write access is
explicit and unavailable to advisory specialists. Native controls are not an
independent operating-system sandbox. Use CLI help for authentication-check
options; installation itself never runs a login or live authentication check.
OpenCode read-only handoffs are disabled; approved write tasks require explicit
subscription attestation, a fully qualified model, matching active cached
credential metadata and a named primary-capable persona. See the
[dispatcher safety and configuration guide](../../docs/dispatcher.md). The
shipped OpenCode routes are intentionally unconfigured and fail closed.
OpenCode subscription verification is being validated; unverified access must
fail closed, not fall back to API billing. Offline commands do not establish
live authentication or model availability.

## Preservation and removal

Installation refuses unmarked directories, symlinked ownership markers or
managed directories/files, hardlinked markers or payloads, and unrelated command
collisions before mutation. Existing managed files must be regular files with
exactly one hard link.
Routing updates create Ansible backups within the owned configuration directory.
An ownership marker must be a regular file with exactly one hard link containing
exactly `ai-agent-workforce:dispatcher` (with an optional final newline).
The old `ai-agent-workforce` marker is accepted only at the original default
`~/.local/share/ai-agent-workforce/dispatcher` path and upgraded on installation.
Legacy custom paths fail closed: verify their ownership explicitly before
replacing the marker with this role's value. Do not relabel another role's storage.
All three managed role roots, shared skills and configured canonical instructions
are checked for overlap before installation or removal, including resolved aliases.

Removal deletes only a matching command symlink and a marked, real dispatcher
directory. Replacement commands and unowned/replaced dispatcher directories
remain untouched. Shared parent directories, instructions, skills and native
client settings/logins remain untouched; existing command-directory permissions
are preserved. Routing backups are removed with the owned dispatcher directory.
Use a dedicated installation directory, not another role's managed directory.
Ownership checks protect against existing collisions, not concurrent filesystem
changes by another process with the same user privileges. Do not run deployment
alongside processes replacing the managed paths.
