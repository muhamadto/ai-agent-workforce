# Cross-CLI Dispatcher Implementation Plan

**Goal:** Delegate a named specialist task from any local Conductor coordinator to Codex, Claude Code or OpenCode using the user's existing CLI logins, not direct provider APIs.

**Architecture:** A Python 3.11+ standard-library dispatcher reads a TOML routing table, checks native CLI prerequisites and runs one non-interactive child in an explicit Git workspace. An opt-in Ansible role installs a private, marked dispatcher directory and an owned `workforce` symlink. Results return as JSON to the coordinator; transient handoff files remain private under the workspace's `.context/` directory.

**Approval:** The user approves implementation, commit and push without further checkpoints, and explicitly exempts this feature from Shortcut's unavailable authentication gate. Do not merge its PR. No packages or direct API credentials are required or installed.

**Security adjustment:** OpenCode read-only execution is disabled because the installed effective policy permits mutations and universal wildcard rules are prohibited. Approved write tasks require user-attested subscription/provider/model/active-credential metadata and a primary-capable native persona. Default OpenCode routes fail closed; this is not a fully working three-provider installation without further local configuration. Codex transport passed live; Claude returned a native credit/access failure, correctly surfaced without fallback. Offline runtime and isolated Ansible checks pass. Delivery remains pending; PR review/merge and the full Definition of Done are not claimed.

## Task 1: Dispatcher and routing

- [ ] Create `config/agent-routing.toml` with all 13 existing specialist names. Route business analysis/principal decisions to Codex, architecture/security/quality/reliability reviews to Claude Sonnet, and implementation specialists to OpenCode. Leave Codex/OpenCode model IDs unset to inherit their configured defaults rather than guessing unavailable models.
- [ ] Add `scripts/dispatch_agent.py` with `list`, `doctor` and `delegate` commands. Support task files/stdin, explicit workspace, optional routing override, dry run, timeout and explicit `--allow-write` opt-in for implementation roles.
- [ ] Use native `codex exec`, `claude -p --agent`, and `opencode run --agent`; never invent a Codex `--agent` flag. Feed Codex its corresponding native TOML persona as task context; require deployed named Claude/OpenCode agents.
- [ ] Reuse cached native subscription authentication. Strip API-key overrides for Codex/Claude children and reject non-subscription native auth. Never extract/reuse credentials in another client or make direct provider API requests.
- [ ] Pass tasks through stdin/private files, not shell interpolation. Use a workspace lock, private transient artifacts, bounded output and whole-process-group timeout cleanup. Return nonzero on native/semantic failures and avoid dumping sensitive native payloads.
- [ ] Default to read-only native controls; refuse write requests for advisory roles. State that CLI tool permissions are not an independent OS sandbox and that external agents not using this dispatcher are not locked.
- [ ] Start with failing offline smoke cases under `.context/` because this repository has no tracked test suite. Cover routing, malformed input, exact argv, billing-auth rejection, native results/errors, timeouts, output limits, locking and redaction without model calls.

## Task 2: Ansible installation

- [ ] Add `roles/dispatcher/{defaults,tasks,templates,README.md}`. Install source, routing and Codex persona payloads at `~/.local/share/ai-agent-workforce/dispatcher/`, plus `~/.local/bin/workforce` linked to a role-owned wrapper.
- [ ] Refuse unmarked directories or unrelated command collisions before changes. Preserve client configuration/authentication, use restrictive modes and back up managed routing updates.
- [ ] Add opt-in `never`/`dispatcher` tags. Test check mode, repeated install/removal and collision/replacement preservation in an isolated home; do not deploy unrelated client settings.

## Task 3: Integration and delivery

- [ ] Update README Project Structure, dispatcher usage, contribution guidance, canonical delegation instructions, and validation of routing/name parity. Keep `.context/` gitignored.
- [ ] Obtain independent specification/security review, fix significant findings, and run Python smoke checks, Ansible syntax/lint and native CLI compatibility checks.
- [ ] Install only the dispatcher and shared instruction update locally through Ansible. Verify installed `list`, `doctor` and dry-run paths; live model tests must remain minimal and disclose any login/quota limitations.
- [ ] Commit with Conventional Commits and Signed-off-by, push the current branch and create/update its review PR. Leave unrelated editor files untouched and never merge automatically.
