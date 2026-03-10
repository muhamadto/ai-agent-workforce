---
name: git-branch
description: Create a branch from latest main, or sync an existing branch with main using rebase — never merge.
---

# Git Branch Skill

Manage branch lifecycle correctly: always cut from `origin/main`, always sync via rebase, never merge.

## When to use

- **Creating a new branch**: ensures you start from the latest main, not a stale local copy
- **Syncing a drifted branch**: brings an existing branch up to date before opening or updating a PR

---

## Scenario A — Create a new branch

### Step 1 — Fetch latest remote state

```bash
git fetch origin
```

Never branch from local `main` — it may be stale. Always branch from `origin/main`.

### Step 2 — Create branch from origin/main

```bash
git checkout -b <branch-name> origin/main
```

Branch naming conventions:

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/<description>` | `feat/user-authentication` |
| Bug fix | `fix/<description>` | `fix/token-expiry-check` |
| Chore | `chore/<description>` | `chore/update-dependencies` |
| Release | `release/<version>` | `release/1.2.0` |

### Step 3 — Push and set upstream

```bash
git push -u origin <branch-name>
```

---

## Scenario B — Sync an existing branch with main

Use this before opening a PR or when main has moved ahead of your branch.

### Step 1 — Save any uncommitted work

```bash
git stash
```

If working tree is clean, skip this step. Check with `git status`.

### Step 2 — Fetch and rebase

```bash
git fetch origin
git rebase origin/main
```

**If conflicts occur during rebase:**

1. Resolve each conflict file — keep your changes, incorporate main's changes
2. Stage the resolved files:
   ```bash
   git add <resolved-file>
   ```
3. Continue the rebase:
   ```bash
   git rebase --continue
   ```
4. If a commit becomes empty after resolution:
   ```bash
   git rebase --skip
   ```
5. To abort and return to the pre-rebase state:
   ```bash
   git rebase --abort
   ```

### Step 3 — Re-apply stashed work

```bash
git stash pop
```

If `stash pop` conflicts with the rebased state, resolve the conflict, then:
```bash
git stash drop
```

### Step 4 — Push (force required after rebase)

```bash
git push --force-with-lease origin <branch-name>
```

Always use `--force-with-lease`, never `--force`. It refuses the push if someone else has pushed to the branch since your last fetch — preventing accidental overwrites.

---

## Safety rules

- Never rebase a branch that others are actively working on — coordinate first
- Never use `--force` without `--lease`
- Never merge `main` into a feature branch — always rebase
- Never branch from local `main` without fetching first
- If rebase produces more than 5 conflicts, stop and investigate — something is structurally wrong
