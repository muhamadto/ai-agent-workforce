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

macOS ACL inspection uses `acl_get_fd_np(..., ACL_TYPE_EXTENDED)`: Apple [acl_file.c](https://raw.githubusercontent.com/apple-oss-distributions/Libc/main/posix1e/acl_file.c) retrieves ACLs using the file descriptor, and [filesec.c](https://raw.githubusercontent.com/apple-oss-distributions/Libc/main/gen/filesec.c) returns `ENOENT` for an absent ACL property. Only this error with an unchanged live descriptor is accepted. Darwin `acl_get_entry` returns zero for an entry, one at end; any entry is refused. `/dev/fd` listings are unsuitable: they omit underlying ACLs on this host.

Synthetic verification:

```sh
python3 -m unittest discover -s tests -p test_fact_cache_containment.py
```

Fixtures cover check/apply/idempotence, real extended ACL rejection, ownership, links, oversized/unknown/duplicate JSON, writable ancestors, FIFO, growth/replacement, safe errors and actual Ansible execution under hostile inherited jsonfile/callback settings. They never open the fixed host caches. This cannot stop an already-open reader or a same-owner privileged process; no claim of prior non-access or revocation is made. Backups or other copies outside these three paths remain unassessed.
