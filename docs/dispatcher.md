# Cross-CLI specialist dispatch

Conductor hosts the coordinator. `workforce` runs a synchronous native CLI
subprocess in the selected Git workspace and returns its final answer as JSON.
It does not create Conductor chats, automatically infer handoffs from messages,
create stories, approve plans, run the review chain or merge PRs. The coordinator
remains responsible for the workflow in `instructions/AGENTS.md`.

## Installation and routing

Use the opt-in [dispatcher role](../roles/dispatcher/README.md). Python 3.11+
and the native CLIs must already be installed. No packages, credentials or
client settings are installed by this role.

`config/agent-routing.toml` maps the same specialist names used by all three
clients. Business analysis and principal engineering use Codex; architecture,
security, quality and reliability reviews use Claude Sonnet; implementation
specialists use OpenCode. Unset model IDs inherit native configuration: neither
a Sol nor a GLM model ID is guessed or promised to be available.

Use `workforce --config /absolute/path/routes.toml ...` or
`WORKFORCE_ROUTING_CONFIG` for alternative routing. Deployment backs up changes
to the installed routing file; personal overrides are best kept outside the
managed installation. `WORKFORCE_CODEX`, `WORKFORCE_CLAUDE` and
`WORKFORCE_OPENCODE` can select existing executable paths.

## Coordinator handoff

```sh
workforce list
workforce doctor
printf '%s\n' 'Review the README and return architecture risks. Do not edit files.' |
  workforce delegate architecture-guardian --workspace "$PWD" --dry-run
printf '%s\n' 'Review the README and return architecture risks. Do not edit files.' |
  workforce delegate architecture-guardian --workspace "$PWD" --timeout 120
```

For larger tasks use `--task-file /absolute/path/task.md`, not command-line
task text. File inputs must be regular UTF-8 files, not symlinks, devices or
FIFOs; reads are bounded to 64 KiB even if a file grows. Keep task files private
and out of Git. A successful response contains
`status`, `agent`, `harness`, requested `model`, `workspace`, `access` and `text`.
`configured-default` describes model selection, not verified model identity.
Failures return nonzero and a safe JSON error; timeout returns 124.

Implementation requires explicit `--allow-write`; advisory architecture and
principal-engineer tasks always refuse it. Write mode retains native permission
checks, so an unapproved tool action may be refused rather than automatically
approved. A completed model response does not establish that acceptance
criteria were met: the coordinator must inspect results and run verification.
Native authentication, quota, model and permission failures are not retried
through another provider.

### OpenCode prerequisite and restriction

OpenCode read-only delegation is disabled. The installed client's effective
policies permit mutations, and adding universal wildcard policies conflicts
with the global operating rules. Do not use `--allow-write` to bypass this
restriction for reviews: route those tasks to Codex or Claude instead.

Approved implementation tasks can use OpenCode with `--allow-write` after the
user explicitly attests their subscription route in a private routing override:

```toml
[agents.backend-developer]
harness = "opencode"
model = "provider/model"
subscription_confirmed = true
credential_id = "id-from-native-auth-list"
```

Replace both placeholders using native `opencode models --standalone` and
`opencode auth list --format json --standalone` metadata. Keep all other specialist
routes when copying the repository routing table. `credential_id` is a non-secret
metadata identifier, never a key or token. The model provider must exactly match
the native integration ID; its first active cached connection must match that
credential ID and use key or OAuth authentication. No credential export or
transfer occurs. The selected model is explicitly passed to the native CLI.

This is **user-attested billing entitlement**, not verification of a purchased
subscription. Cached key credentials can belong to subscription services. The
user must confirm the actual model/connection is covered and review spending
limits; the dispatcher cannot establish those from login metadata. There is no
automatic fallback, but native provider configuration remains trusted input.
The shipped OpenCode routes intentionally lack this attestation and refuse live
tasks until the user configures them. This feature is not a fully working
three-provider installation out of the box.

Codex is restricted to its built-in OpenAI provider and ChatGPT authentication
for each invocation. Claude requires a claude.ai login, refuses configured
API-key helpers and clears API/cloud-provider environment overrides in the
child and its runtime settings. These checks do not establish remaining quota
or disable a subscription's separately enabled extra-usage billing. Account
spending limits remain the user's responsibility.

Codex receives its bundled TOML `developer_instructions` as specialist context
for `codex exec`, not a fabricated `--agent` flag. Claude and OpenCode require
their named personas to be deployed through the corresponding roles.

## Safety boundaries

- Tasks travel through stdin or private files, never shell interpolation.
- Handoffs use `0700` directories and `0600` files under the canonical Git
  worktree's `.context/workforce/`. Subdirectory calls share its exclusive lock.
- Handoff files are created exclusively without following symlinks. Shared
  hardlinks and redirected output files are refused rather than overwritten.
- Normal completion, failures, timeout and catchable termination clean transient
  jobs and stop the child process group. SIGKILL or a machine crash cannot run
  cleanup; inspect leftover private jobs before manually deleting them.
- Output is limited to 2 MiB, tasks to 64 KiB and timeout to at most one hour.
  Stdout and stderr share a bounded pipe collector; over-limit bytes are never
  written to handoff files. Codex's final message comes from its JSONL stream,
  not a separately CLI-written result file.
- Nested `workforce` delegation is refused. Delegates are instructed not to
  commit, push, deploy or disclose sensitive information.
- Known environment secrets, private-key blocks and common token patterns are
  redacted from returned text. This is best-effort filtering, not a guarantee
  that arbitrary sensitive content can be recognised. Never send secrets as
  tasks or request secret-bearing output.
- Native CLI history and provider retention still apply; transient-file cleanup
  is not deletion of native sessions or remote data.
- CLI tool permissions are not an independent operating-system sandbox. Only
  use trusted personas, workspace instructions, executable overrides, plugins
  and configuration. The lock cannot protect against unrelated agents, escaped
  descendant sessions or processes that bypass the dispatcher.

Run `doctor` before delegating. It checks prerequisites without a model request,
including each authenticated OpenCode route's effective primary-execution
persona, but does not establish subscription quota or live model availability.
