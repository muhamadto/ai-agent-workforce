# Fact-cache containment — Shortcut 742

Stage one restricts the **three fixed, recognised** `s1_localhost` caches to owner read/write (`0600`). It does not delete them, revoke credentials or establish whether earlier access occurred. Rotate the exposed Shortcut credential after containment. Permanent memory-only caching and minimal fact gathering remain separate work; do not resume the existing guidance play yet.

After independent source review and commit, from the repository root:

```sh
python3 containment/run_containment.py --check
python3 containment/run_containment.py
python3 containment/run_containment.py
```

The launcher accepts only `--check`, discards ambient Ansible options, plugins and credentials, selects the dedicated memory-cache configuration, and runs a local play with no fact gathering. Temporary execution files use Python's private temporary directory. The play reports metadata only; task output is protected by `no_log`. A second successful apply must report no changes.

The helper checks no-follow directory/file descriptors, ancestor ownership and write permissions, regular single-link owner files, a 16 MiB bound, Ansible's JSON `__payload__` wrapper and environment/python/gather-subset shape. It verifies identities around same-descriptor `fchmod`, and refuses extended ACLs both before and after containment. Missing files are unchanged. Any unknown shape, ACL, link, ownership, race or inspection error stops with a sanitised failure; investigate privately rather than broadening access or deleting unknown files. Partial containment remains possible if a later target fails; retain and report successful earlier restrictions, then fix the refusal in code.

macOS ACL inspection uses `acl_get_fd_np(..., ACL_TYPE_EXTENDED)`: Apple [acl_file.c](https://raw.githubusercontent.com/apple-oss-distributions/Libc/main/posix1e/acl_file.c) retrieves ACLs using the file descriptor, and [filesec.c](https://raw.githubusercontent.com/apple-oss-distributions/Libc/main/gen/filesec.c) returns `ENOENT` for an absent ACL property. Only this error with an unchanged live descriptor is accepted. Darwin `acl_get_entry` returns zero for an entry; any entry is refused. An empty ACL object is conservatively refused; only a verified absent ACL is accepted. `/dev/fd` listings are unsuitable: they omit underlying ACLs on this host.

Synthetic verification:

```sh
python3 -m unittest discover -s .context/auxiliary-tests -p test_fact_cache_containment.py
```

Fixtures cover check/apply/idempotence, real extended ACL rejection, ownership, links, oversized/unknown/duplicate JSON, writable ancestors, FIFO, growth/replacement, safe errors and actual Ansible execution under hostile inherited jsonfile/callback settings. They never open the fixed host caches. This cannot stop an already-open reader or a same-owner privileged process; no claim of prior non-access or revocation is made. Backups or other copies outside these three paths remain unassessed.

## Permanent prevention stage

Repository caching is memory-only; guidance gathers only user/python facts and the workforce root play adds system facts for its macOS guard. Supported workforce execution is `python3 run_playbook.py guidance [--check] [--diff]`; the optional `workforce` selection remains a full deployment and requires its own approval. The launcher uses the operating-system user home and a fixed execution PATH, a private local inventory, the absolute repository configuration and a credential-free environment. Unknown options return a generic error. It accepts only check/diff and bounded tag selections; no arbitrary inventory, variables, plugins or remote targets.

After source review, signed commits and PR checks, the configuration-only delivery command is:

```sh
python3 containment/deliver_prevention.py --check
python3 containment/deliver_prevention.py
python3 containment/deliver_prevention.py
```

The fixed reviewed plan guards eight existing source files by complete before/after SHA-256 and exact replacement counts. It removes persistent cache settings, narrows facts and replaces only environment HOME references. Owner browser comments and all other bytes remain intact. It creates only two fixed root `run_playbook.py` files, absent or already exactly reviewed, using an absent-only atomic link. It never invokes either root play or installs packages. Existing files are atomically replaced while preserving their modes; ACLs, owner, links, bounded contents and descriptor/path identities are checked. Directory ACLs may contain deny entries only; any allow or unknown entry refuses. Staging cleanup removes only the recognised stage inode and leaves unknown replacements untouched. All targets are prevalidated before writes; subsequent changes can still cause a partial delivery, which is reported as failure.

The owner mac-setup entry point after delivery is `python3 /Users/matto/Workspace/mac-setup/run_playbook.py --check --tags devtools`. The owner workforce launcher must wait for its selected reviewed play to reach that root checkout; this delivery does not copy the guidance play there. Do not execute root roles merely to verify configuration. The guarded play for the pending guidance refresh can be run from this worktree with `python3 run_playbook.py guidance --check`, then the reviewed apply and idempotence run.

Linux CI exercises portable path/content guards with an explicit emulated macOS ACL boundary. Real ACL fixtures are labelled macOS-only; macOS execution proves the actual ACL boundary. Neither production helper supports Linux host delivery, and no temporary-directory security exception was widened to fix CI.

Story 750 adds verified SSH host trust to both source configurations and forces `ANSIBLE_HOST_KEY_CHECKING=True` in both supported launchers, despite inherited false settings. Synthetic local Ansible assertions check the effective setting without opening an SSH connection. Any separately approved remote execution requires trusted, independently verified known_hosts provisioning; unknown or changed keys must fail. No trust-store mutation, automatic acceptance or remote connection is part of this delivery.
